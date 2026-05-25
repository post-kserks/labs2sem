from __future__ import annotations

import cv2
import numpy as np


def _find_separator_row(image: np.ndarray) -> int:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    row_density = (gray < 200).mean(axis=1).astype(np.float32)

    smoothed = cv2.GaussianBlur(row_density.reshape(-1, 1), (1, 31), 0).reshape(-1)
    height = image.shape[0]

    start = height // 4
    end = (height * 3) // 4
    local_min_idx = int(np.argmin(smoothed[start:end])) + start
    return local_min_idx


def _trim_panel(panel: np.ndarray) -> np.ndarray:
    gray = cv2.cvtColor(panel, cv2.COLOR_BGR2GRAY)
    non_background = gray < 245

    row_activity = non_background.mean(axis=1)
    col_activity = non_background.mean(axis=0)

    row_indices = np.where(row_activity > 0.02)[0]
    col_indices = np.where(col_activity > 0.02)[0]

    if row_indices.size == 0 or col_indices.size == 0:
        return panel

    y1 = max(0, int(row_indices[0]) - 2)
    y2 = min(panel.shape[0], int(row_indices[-1]) + 3)
    x1 = max(0, int(col_indices[0]) - 2)
    x2 = min(panel.shape[1], int(col_indices[-1]) + 3)

    return panel[y1:y2, x1:x2]


def split_into_panels(image: np.ndarray) -> tuple[np.ndarray, np.ndarray, int]:
    separator_row = _find_separator_row(image)

    gap = max(6, int(round(image.shape[0] * 0.01)))
    upper = image[: max(1, separator_row - gap), :]
    lower = image[min(image.shape[0] - 1, separator_row + gap) :, :]

    upper = _trim_panel(upper)
    lower = _trim_panel(lower)

    return upper, lower, separator_row
