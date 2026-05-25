from __future__ import annotations

import cv2
import numpy as np


def _build_curve_mask(panel: np.ndarray, dark_threshold: int) -> np.ndarray:
    blue, green, red = cv2.split(panel)
    red_mask = (red.astype(np.int16) - green.astype(np.int16) > 12) & (
        red.astype(np.int16) - blue.astype(np.int16) > 18
    ) & (red > 85)

    gray = cv2.cvtColor(panel, cv2.COLOR_BGR2GRAY)
    dark_mask = gray < dark_threshold

    red_dilated = cv2.dilate(red_mask.astype(np.uint8), np.ones((3, 3), np.uint8), iterations=1) > 0
    curve_mask = dark_mask & (~red_dilated)

    curve_mask_u8 = (curve_mask.astype(np.uint8) * 255)
    curve_mask_u8 = cv2.medianBlur(curve_mask_u8, 3)

    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(curve_mask_u8, connectivity=8)
    filtered = np.zeros_like(curve_mask_u8)

    for label in range(1, num_labels):
        area = stats[label, cv2.CC_STAT_AREA]
        if area >= 8:
            filtered[labels == label] = 255

    return filtered > 0


def _track_curve_y(mask: np.ndarray, max_jump_px: int, smoothing_window: int) -> np.ndarray:
    height, width = mask.shape
    y_track = np.full(width, np.nan, dtype=np.float32)

    row_weights = mask.sum(axis=1).astype(np.float32)
    if float(row_weights.sum()) > 0.0:
        row_indices = np.arange(height, dtype=np.float32)
        reference_y = float(np.average(row_indices, weights=row_weights))
    else:
        reference_y = float(height // 2)

    previous_y: float | None = reference_y

    for x in range(width):
        candidates = np.where(mask[:, x])[0]
        if candidates.size == 0:
            continue

        deltas_prev = np.abs(candidates.astype(np.float32) - float(previous_y))
        deltas_ref = np.abs(candidates.astype(np.float32) - reference_y)
        scores = deltas_prev + (0.25 * deltas_ref)

        best_index = int(np.argmin(scores))
        if deltas_prev[best_index] > max_jump_px:
            # Hard jump most likely belongs to text/noise; keep last estimate.
            y_value = float(previous_y)
        else:
            y_value = float(candidates[best_index])

        y_track[x] = y_value
        previous_y = y_value

    valid_mask = ~np.isnan(y_track)
    if not valid_mask.any():
        raise ValueError("Failed to track curve: no valid points detected.")

    x_coords = np.arange(width, dtype=np.float32)
    y_interpolated = np.interp(x_coords, x_coords[valid_mask], y_track[valid_mask]).astype(np.float32)

    if smoothing_window > 1:
        if smoothing_window % 2 == 0:
            smoothing_window += 1
        y_interpolated = cv2.GaussianBlur(
            y_interpolated.reshape(1, -1),
            (smoothing_window, 1),
            sigmaX=0,
        ).reshape(-1)

    return np.clip(y_interpolated, 0, height - 1)


def extract_curve(
    panel: np.ndarray,
    dark_threshold: int,
    max_jump_px: int,
    smoothing_window: int,
    row_start_ratio: float,
    row_end_ratio: float,
) -> tuple[np.ndarray, np.ndarray]:
    mask = _build_curve_mask(panel, dark_threshold=dark_threshold)
    height = mask.shape[0]

    row_start = max(0, int(height * row_start_ratio))
    row_end = min(height, int(height * row_end_ratio))
    constrained = np.zeros_like(mask)
    constrained[row_start:row_end, :] = mask[row_start:row_end, :]

    y_track = _track_curve_y(mask=constrained, max_jump_px=max_jump_px, smoothing_window=smoothing_window)
    return y_track, (constrained.astype(np.uint8) * 255)
