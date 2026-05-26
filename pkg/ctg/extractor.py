from __future__ import annotations

import cv2
import numpy as np

from internal.domain.models import CTGMetadata, ImageProcessingSpec
from pkg.ctg.preprocess import dered_and_inpaint


def _filter_small_components(mask: np.ndarray, min_area: int) -> np.ndarray:
    num_labels, labels, stats, _ = cv2.connectedComponentsWithStats(mask, connectivity=8)
    filtered = np.zeros_like(mask)
    for label in range(1, num_labels):
        if stats[label, cv2.CC_STAT_AREA] >= min_area:
            filtered[labels == label] = 255
    return filtered


def _build_signal_mask(
    degrid_gray: np.ndarray,
    hsv: np.ndarray,
    red_mask: np.ndarray,
    spec: ImageProcessingSpec,
    mode: str,
) -> tuple[np.ndarray, np.ndarray]:
    mask_dark_hsv = cv2.inRange(hsv, (0, 0, 0), (180, 175, spec.dark_v_max))

    _, otsu = cv2.threshold(degrid_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
    adaptive = cv2.adaptiveThreshold(
        degrid_gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        7,
    )

    dark_mask = cv2.bitwise_or(mask_dark_hsv, otsu)
    dark_mask = cv2.bitwise_or(dark_mask, adaptive)

    red_dilate_size = 3 if mode == "strict" else 1
    red_dilated = cv2.dilate(
        red_mask,
        cv2.getStructuringElement(cv2.MORPH_RECT, (red_dilate_size, red_dilate_size)),
        iterations=1,
    )

    signal = cv2.bitwise_and(dark_mask, cv2.bitwise_not(red_dilated))

    close_kernel = (3, 1) if mode == "strict" else (5, 1)
    signal = cv2.morphologyEx(signal, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, close_kernel))
    signal = cv2.morphologyEx(signal, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2)))

    min_area = 10 if mode == "strict" else 6
    signal = _filter_small_components(signal, min_area=min_area)

    return signal, dark_mask


def separate_signal_from_grid(
    image_bgr: np.ndarray,
    spec: ImageProcessingSpec,
    mode: str = "strict",
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    degrid_bgr, degrid_gray, red_mask = dered_and_inpaint(image_bgr, spec)
    hsv = cv2.cvtColor(degrid_bgr, cv2.COLOR_BGR2HSV)

    signal, dark_mask = _build_signal_mask(
        degrid_gray=degrid_gray,
        hsv=hsv,
        red_mask=red_mask,
        spec=spec,
        mode=mode,
    )

    return signal, red_mask, dark_mask, degrid_gray


def split_fhr_toco_masks(signal_mask: np.ndarray, metadata: CTGMetadata, mode: str = "strict") -> tuple[np.ndarray, np.ndarray]:
    height = signal_mask.shape[0]

    sep_top = max(1, min(height - 2, metadata.separator_y_top))
    sep_bottom = max(sep_top + 1, min(height - 1, metadata.separator_y_bottom))

    fhr_mask = np.zeros_like(signal_mask)
    toco_mask = np.zeros_like(signal_mask)

    fhr_mask[:sep_top, :] = signal_mask[:sep_top, :]
    toco_mask[sep_bottom:, :] = signal_mask[sep_bottom:, :]

    min_area = 8 if mode == "strict" else 5
    fhr_mask = _filter_small_components(fhr_mask, min_area=min_area)
    toco_mask = _filter_small_components(toco_mask, min_area=min_area)

    return fhr_mask, toco_mask
