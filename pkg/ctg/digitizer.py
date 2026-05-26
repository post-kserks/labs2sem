from __future__ import annotations

import cv2
import numpy as np
import pandas as pd

from internal.domain.models import AxisSpec, CTGMetadata, DigitizationResult, ExtractedSeries, ImageProcessingSpec, TimeSpec
from pkg.ctg.tracker_dp import track_curve_dp


def _pixel_to_value(y_px: float, y_min_px: int, y_max_px: int, val_min: float, val_max: float) -> float:
    denominator = float(y_min_px - y_max_px)
    if abs(denominator) < 1e-6:
        return float((val_min + val_max) * 0.5)

    value = val_max - ((y_px - y_max_px) / denominator) * (val_max - val_min)
    return float(np.clip(value, val_min, val_max))


def _track_to_values(track_y: np.ndarray, y_min_px: int, y_max_px: int, axis: AxisSpec) -> np.ndarray:
    values = np.array(
        [_pixel_to_value(y, y_min_px, y_max_px, axis.min_value, axis.max_value) for y in track_y],
        dtype=np.float32,
    )
    return values


def _postprocess(values: np.ndarray, spec: ImageProcessingSpec, axis: AxisSpec) -> np.ndarray:
    series = pd.Series(values)

    window = max(1, spec.median_filter_window)
    if window % 2 == 0:
        window += 1

    series = series.rolling(window=window, center=True, min_periods=1).median()
    smoothed = series.to_numpy(dtype=np.float32)

    # Light Gaussian smoothing to reduce staircase artifacts from pixel-level tracking.
    gaussian_window = max(3, window + 2)
    if gaussian_window % 2 == 0:
        gaussian_window += 1
    smoothed = cv2.GaussianBlur(smoothed.reshape(1, -1), (gaussian_window, 1), 0).reshape(-1).astype(np.float32)
    return np.clip(smoothed, axis.min_value, axis.max_value)


def digitize_ctg(
    fhr_mask: np.ndarray,
    toco_mask: np.ndarray,
    metadata: CTGMetadata,
    upper_axis: AxisSpec,
    lower_axis: AxisSpec,
    time_spec: TimeSpec,
    image_spec: ImageProcessingSpec,
    guidance_gray: np.ndarray | None = None,
) -> DigitizationResult:
    if fhr_mask.shape != toco_mask.shape:
        raise ValueError("FHR and TOCO masks must have identical dimensions.")

    height, width = fhr_mask.shape

    max_step = max(3, min(12, int(round(image_spec.max_tracking_jump_px * 0.15))))

    fhr_track = track_curve_dp(
        mask=fhr_mask,
        band_top=max(0, min(metadata.fhr_y_min, metadata.fhr_y_max)),
        band_bottom=min(height, max(metadata.fhr_y_min, metadata.fhr_y_max) + 1),
        max_step_px=max_step,
        gray_image=guidance_gray,
    )
    toco_track = track_curve_dp(
        mask=toco_mask,
        band_top=max(0, min(metadata.toco_y_min, metadata.toco_y_max)),
        band_bottom=min(height, max(metadata.toco_y_min, metadata.toco_y_max) + 1),
        max_step_px=max_step,
        gray_image=guidance_gray,
    )

    fhr_native = _track_to_values(fhr_track, metadata.fhr_y_min, metadata.fhr_y_max, upper_axis)
    toco_native = _track_to_values(toco_track, metadata.toco_y_min, metadata.toco_y_max, lower_axis)

    fhr_native = _postprocess(fhr_native, spec=image_spec, axis=upper_axis)
    toco_native = _postprocess(toco_native, spec=image_spec, axis=lower_axis)

    original_time = np.arange(width, dtype=np.float32) / max(metadata.px_per_minute, 1e-6)

    step_min = max(1e-4, float(time_spec.sampling_step_seconds) / 60.0)
    duration_min = max(float(time_spec.duration_minutes), float(original_time[-1]) if width > 1 else 0.0)
    target_time = np.arange(0.0, duration_min + (step_min * 0.5), step_min, dtype=np.float32)

    fhr_resampled = np.interp(target_time, original_time, fhr_native).astype(np.float32)
    toco_resampled = np.interp(target_time, original_time, toco_native).astype(np.float32)

    return DigitizationResult(
        series=ExtractedSeries(
            time_min=target_time,
            fhr_bpm=fhr_resampled,
            toco_units=toco_resampled,
        ),
        fhr_track_y=fhr_track,
        toco_track_y=toco_track,
        fhr_values_native=fhr_native,
        toco_values_native=toco_native,
    )
