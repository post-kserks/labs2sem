from __future__ import annotations

import cv2
import numpy as np

from internal.domain.models import ImageProcessingSpec


def build_red_mask(image_bgr: np.ndarray, spec: ImageProcessingSpec) -> np.ndarray:
    hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV)
    blue, green, red = cv2.split(image_bgr)

    mask_red_1 = cv2.inRange(
        hsv,
        (spec.red_hue_low_1, spec.red_s_min, spec.red_v_min),
        (spec.red_hue_high_1, 255, 255),
    )
    mask_red_2 = cv2.inRange(
        hsv,
        (spec.red_hue_low_2, spec.red_s_min, spec.red_v_min),
        (spec.red_hue_high_2, 255, 255),
    )
    mask_hsv = cv2.bitwise_or(mask_red_1, mask_red_2)

    mask_rgb = (
        (
            (red.astype(np.int16) - green.astype(np.int16) > 12)
            & (red.astype(np.int16) - blue.astype(np.int16) > 18)
            & (red > 85)
        )
        .astype(np.uint8)
        * 255
    )

    mask = cv2.bitwise_or(mask_hsv, mask_rgb)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
    return mask


def dered_and_inpaint(image_bgr: np.ndarray, spec: ImageProcessingSpec) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    red_mask = build_red_mask(image_bgr, spec)
    inpaint_mask = cv2.dilate(red_mask, cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3)), iterations=1)

    # Fill red-grid regions with neighboring texture to preserve dark signal continuity.
    degrid_bgr = cv2.inpaint(image_bgr, inpaint_mask, 3, cv2.INPAINT_TELEA)
    degrid_gray = cv2.cvtColor(degrid_bgr, cv2.COLOR_BGR2GRAY)

    clahe = cv2.createCLAHE(
        clipLimit=spec.clahe_clip_limit,
        tileGridSize=(spec.clahe_tile_size, spec.clahe_tile_size),
    )
    degrid_gray = clahe.apply(degrid_gray)

    return degrid_bgr, degrid_gray, red_mask
