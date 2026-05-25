from __future__ import annotations

import numpy as np

from internal.domain.models import AxisSpec, ExtractedSeries, TimeSpec


def _pixels_to_values(y_pixels: np.ndarray, panel_height: int, axis: AxisSpec) -> np.ndarray:
    if panel_height <= 1:
        raise ValueError("Panel height must be greater than 1 pixel for calibration.")

    normalized = y_pixels / float(panel_height - 1)
    values = axis.max_value - normalized * (axis.max_value - axis.min_value)
    return values.astype(np.float32)


def _build_uniform_time_axis(duration_minutes: float, step_seconds: float) -> np.ndarray:
    duration_seconds = max(1.0, duration_minutes * 60.0)
    if step_seconds <= 0:
        raise ValueError("sampling_step_seconds must be positive")

    points = int(np.floor(duration_seconds / step_seconds)) + 1
    return np.linspace(0.0, duration_seconds, points, dtype=np.float32)


def build_extracted_series(
    upper_y_pixels: np.ndarray,
    lower_y_pixels: np.ndarray,
    upper_panel_height: int,
    lower_panel_height: int,
    upper_axis: AxisSpec,
    lower_axis: AxisSpec,
    time_spec: TimeSpec,
) -> ExtractedSeries:
    width = min(len(upper_y_pixels), len(lower_y_pixels))
    if width < 2:
        raise ValueError("Not enough points to build time series.")

    upper_trimmed = upper_y_pixels[:width]
    lower_trimmed = lower_y_pixels[:width]

    upper_values = _pixels_to_values(upper_trimmed, upper_panel_height, upper_axis)
    lower_values = _pixels_to_values(lower_trimmed, lower_panel_height, lower_axis)

    total_seconds = max(1.0, time_spec.duration_minutes * 60.0)
    original_time = np.linspace(0.0, total_seconds, width, dtype=np.float32)
    target_time = _build_uniform_time_axis(
        duration_minutes=time_spec.duration_minutes,
        step_seconds=time_spec.sampling_step_seconds,
    )

    upper_resampled = np.interp(target_time, original_time, upper_values).astype(np.float32)
    lower_resampled = np.interp(target_time, original_time, lower_values).astype(np.float32)

    return ExtractedSeries(
        time_seconds=target_time,
        upper_values=upper_resampled,
        lower_values=lower_resampled,
    )
