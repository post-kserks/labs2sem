from __future__ import annotations

import math

import cv2
import numpy as np


def _rotate_with_bounds(image: np.ndarray, angle_degrees: float) -> np.ndarray:
    height, width = image.shape[:2]
    center = (width / 2.0, height / 2.0)

    rotation_matrix = cv2.getRotationMatrix2D(center, angle_degrees, 1.0)
    abs_cos = abs(rotation_matrix[0, 0])
    abs_sin = abs(rotation_matrix[0, 1])

    new_width = int((height * abs_sin) + (width * abs_cos))
    new_height = int((height * abs_cos) + (width * abs_sin))

    rotation_matrix[0, 2] += (new_width / 2.0) - center[0]
    rotation_matrix[1, 2] += (new_height / 2.0) - center[1]

    return cv2.warpAffine(
        image,
        rotation_matrix,
        (new_width, new_height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )


def _estimate_skew_angle(image: np.ndarray, min_line_length_ratio: float) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, 70, 200)

    min_line_length = max(40, int(image.shape[1] * min_line_length_ratio))
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=110,
        minLineLength=min_line_length,
        maxLineGap=20,
    )

    if lines is None:
        return 0.0

    angles: list[float] = []
    for line in lines[:, 0]:
        x1, y1, x2, y2 = line
        dx = x2 - x1
        dy = y2 - y1
        if dx == 0 and dy == 0:
            continue

        angle = math.degrees(math.atan2(dy, dx))
        normalized = ((angle + 90.0) % 180.0) - 90.0

        # Horizontal-ish lines are the strongest indicator of skew for chart paper.
        if abs(normalized) <= 45.0:
            angles.append(normalized)

    if not angles:
        return 0.0

    return float(np.median(np.array(angles, dtype=np.float32)))


def align_chart_image(image: np.ndarray, min_line_length_ratio: float = 0.35) -> tuple[np.ndarray, float]:
    if image.shape[0] > image.shape[1]:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    skew_angle = _estimate_skew_angle(image, min_line_length_ratio=min_line_length_ratio)

    if abs(skew_angle) < 0.2:
        return image, 0.0

    corrected = _rotate_with_bounds(image, -skew_angle)
    return corrected, skew_angle
