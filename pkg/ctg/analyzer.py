from __future__ import annotations

import cv2
import numpy as np

from internal.domain.models import CTGMetadata, PipelineConfig
from pkg.ctg.preprocess import build_red_mask


def _build_red_mask(image: np.ndarray, config: PipelineConfig) -> np.ndarray:
    return build_red_mask(image, config.image_spec)


def _smooth_profile(profile: np.ndarray, kernel_size: int) -> np.ndarray:
    kernel_size = max(3, kernel_size)
    if kernel_size % 2 == 0:
        kernel_size += 1
    return cv2.GaussianBlur(profile.reshape(-1, 1), (1, kernel_size), 0).reshape(-1)


def _extract_peak_positions(profile: np.ndarray, threshold: float) -> np.ndarray:
    active = profile >= threshold
    if not np.any(active):
        return np.array([], dtype=np.int32)

    transitions = np.diff(active.astype(np.int8), prepend=0, append=0)
    starts = np.where(transitions == 1)[0]
    ends = np.where(transitions == -1)[0]

    centers = []
    for start, end in zip(starts, ends):
        if end <= start:
            continue
        segment = profile[start:end]
        center = start + int(np.argmax(segment))
        centers.append(center)

    return np.array(centers, dtype=np.int32)


def _estimate_spacing(positions: np.ndarray, fallback: float) -> float:
    if positions.size < 2:
        return max(1.0, fallback)

    diffs = np.diff(np.sort(positions)).astype(np.float32)
    diffs = diffs[(diffs > 1.0) & (diffs < 500.0)]

    if diffs.size == 0:
        return max(1.0, fallback)

    candidate = float(np.median(diffs))

    # Candidate may correspond to minor cell; map to closest major-step hypothesis.
    hypotheses = []
    for mul in (1.0, 2.0, 3.0, 4.0, 5.0):
        hypotheses.append(candidate * mul)
        hypotheses.append(candidate / mul)

    best = min(hypotheses, key=lambda value: abs(value - fallback))
    if best < fallback * 0.55 or best > fallback * 1.8:
        return max(1.0, fallback)

    return max(1.0, float(best))


def detect_separator_band(image: np.ndarray, red_mask: np.ndarray) -> tuple[int, int]:
    height = image.shape[0]
    row_red = red_mask.mean(axis=1).astype(np.float32) / 255.0
    smoothed = _smooth_profile(row_red, kernel_size=max(11, int(height * 0.04)))

    search_top = int(height * 0.25)
    search_bottom = int(height * 0.75)
    local = smoothed[search_top:search_bottom]

    min_idx = int(np.argmin(local)) + search_top
    baseline = float(np.median(smoothed[search_top:search_bottom]))
    threshold = min(float(smoothed[min_idx]) + 0.35 * (baseline - float(smoothed[min_idx])), baseline)

    top = min_idx
    bottom = min_idx
    while top > 0 and smoothed[top] <= threshold:
        top -= 1
    while bottom < height - 1 and smoothed[bottom] <= threshold:
        bottom += 1

    if bottom - top < max(6, int(height * 0.01)):
        pad = max(4, int(height * 0.01))
        top = max(0, min_idx - pad)
        bottom = min(height - 1, min_idx + pad)

    return top, bottom


def _panel_scale(
    red_mask: np.ndarray,
    top: int,
    bottom: int,
    value_min: float,
    value_max: float,
    major_step: float,
) -> tuple[float, int, int]:
    panel = red_mask[top:bottom, :]
    if panel.size == 0:
        panel_height = max(1, bottom - top)
        fallback_major = panel_height / max(1.0, (value_max - value_min) / max(1.0, major_step))
        px_per_unit = fallback_major / max(1.0, major_step)
        return px_per_unit, top, bottom - 1

    projection = panel.sum(axis=1).astype(np.float32)
    threshold = float(np.percentile(projection, 85) * 0.50)
    peaks = _extract_peak_positions(projection, threshold=threshold)

    panel_height = max(1, bottom - top)
    fallback_major = (panel_height * 0.90) / max(1.0, (value_max - value_min) / max(1.0, major_step))
    major_spacing = _estimate_spacing(peaks, fallback=fallback_major)

    px_per_unit = major_spacing / max(1.0, major_step)

    expected_span = int(round((value_max - value_min) * px_per_unit))
    max_span = int(panel_height * 0.94)
    min_span = int(panel_height * 0.70)
    expected_span = max(min_span, min(max_span, expected_span))

    top_margin = max(2, int(panel_height * 0.03))
    y_top = top + top_margin
    y_bottom = y_top + expected_span
    if y_bottom >= bottom:
        y_bottom = bottom - 1
        y_top = max(top, y_bottom - expected_span)

    return float(px_per_unit), int(y_top), int(y_bottom)


def _estimate_time_scale(red_mask: np.ndarray, expected_duration: float) -> float:
    width = red_mask.shape[1]
    projection = red_mask.sum(axis=0).astype(np.float32)

    threshold = float(np.percentile(projection, 85) * 0.55)
    peaks = _extract_peak_positions(projection, threshold=threshold)

    fallback = width / max(1.0, expected_duration)
    spacing = _estimate_spacing(peaks, fallback=fallback)

    if spacing < fallback * 0.6 or spacing > fallback * 1.6:
        return fallback

    return spacing


def analyze_ctg_layout(image: np.ndarray, config: PipelineConfig) -> CTGMetadata:
    red_mask = _build_red_mask(image, config)

    sep_top, sep_bottom = detect_separator_band(image, red_mask)

    upper_top = 0
    upper_bottom = max(upper_top + 2, sep_top)
    lower_top = min(image.shape[0] - 2, sep_bottom + 1)
    lower_bottom = image.shape[0]

    px_per_unit_fhr, fhr_y_max, fhr_y_min = _panel_scale(
        red_mask=red_mask,
        top=upper_top,
        bottom=upper_bottom,
        value_min=config.upper_axis.min_value,
        value_max=config.upper_axis.max_value,
        major_step=config.upper_axis.major_step,
    )
    px_per_unit_toco, toco_y_max, toco_y_min = _panel_scale(
        red_mask=red_mask,
        top=lower_top,
        bottom=lower_bottom,
        value_min=config.lower_axis.min_value,
        value_max=config.lower_axis.max_value,
        major_step=config.lower_axis.major_step,
    )

    px_per_minute = _estimate_time_scale(red_mask=red_mask, expected_duration=config.time_spec.duration_minutes)
    duration_minutes = float(image.shape[1]) / max(px_per_minute, 1e-6)

    # Without explicit DPI or OCR-confirmed labels, we use a pragmatic threshold.
    paper_speed_cm_per_min = 3.0 if px_per_minute >= 75.0 else 1.0

    return CTGMetadata(
        px_per_minute=float(px_per_minute),
        px_per_unit_fhr=float(px_per_unit_fhr),
        px_per_unit_toco=float(px_per_unit_toco),
        fhr_y_min=int(fhr_y_min),
        fhr_y_max=int(fhr_y_max),
        toco_y_min=int(toco_y_min),
        toco_y_max=int(toco_y_max),
        separator_y_top=int(sep_top),
        separator_y_bottom=int(sep_bottom),
        time_start=config.time_spec.start_timestamp,
        duration_minutes=float(duration_minutes),
        paper_speed_cm_per_min=float(paper_speed_cm_per_min),
    )
