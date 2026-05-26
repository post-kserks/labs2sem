from __future__ import annotations

import math

import cv2
import numpy as np

from internal.domain.models import AlignmentResult, ImageProcessingSpec


def _order_quad_points(points: np.ndarray) -> np.ndarray:
    points = points.astype(np.float32)
    sums = points.sum(axis=1)
    diffs = np.diff(points, axis=1).reshape(-1)

    top_left = points[np.argmin(sums)]
    bottom_right = points[np.argmax(sums)]
    top_right = points[np.argmin(diffs)]
    bottom_left = points[np.argmax(diffs)]

    return np.array([top_left, top_right, bottom_right, bottom_left], dtype=np.float32)


def _rotate_with_bounds(image: np.ndarray, angle_degrees: float) -> np.ndarray:
    height, width = image.shape[:2]
    center = (width / 2.0, height / 2.0)

    matrix = cv2.getRotationMatrix2D(center, angle_degrees, 1.0)
    abs_cos = abs(matrix[0, 0])
    abs_sin = abs(matrix[0, 1])

    new_width = int((height * abs_sin) + (width * abs_cos))
    new_height = int((height * abs_cos) + (width * abs_sin))

    matrix[0, 2] += (new_width / 2.0) - center[0]
    matrix[1, 2] += (new_height / 2.0) - center[1]

    return cv2.warpAffine(
        image,
        matrix,
        (new_width, new_height),
        flags=cv2.INTER_LINEAR,
        borderMode=cv2.BORDER_REPLICATE,
    )


def _estimate_skew_angle(image: np.ndarray, spec: ImageProcessingSpec) -> float:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(
        clipLimit=spec.clahe_clip_limit,
        tileGridSize=(spec.clahe_tile_size, spec.clahe_tile_size),
    )
    normalized = clahe.apply(gray)
    edges = cv2.Canny(normalized, spec.canny_low, spec.canny_high)

    min_len = max(40, int(image.shape[1] * spec.min_line_length_ratio))
    lines = cv2.HoughLinesP(
        edges,
        rho=1,
        theta=np.pi / 180,
        threshold=100,
        minLineLength=min_len,
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
        normalized_angle = ((angle + 90.0) % 180.0) - 90.0
        if abs(normalized_angle) <= 25.0:
            angles.append(normalized_angle)

    if not angles:
        return 0.0

    return float(np.median(np.array(angles, dtype=np.float32)))


def _detect_perspective_quad(image: np.ndarray, spec: ImageProcessingSpec) -> np.ndarray | None:
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blurred, spec.canny_low, spec.canny_high)

    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    edges = cv2.dilate(edges, kernel, iterations=1)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    image_area = float(image.shape[0] * image.shape[1])
    min_area = image_area * spec.perspective_min_area_ratio

    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    for contour in contours[:10]:
        area = float(cv2.contourArea(contour))
        if area < min_area:
            continue

        peri = cv2.arcLength(contour, True)
        approx = cv2.approxPolyDP(contour, 0.02 * peri, True)

        if len(approx) == 4:
            return _order_quad_points(approx.reshape(4, 2))

        box = cv2.boxPoints(cv2.minAreaRect(contour))
        return _order_quad_points(box)

    return None


def _warp_from_quad(image: np.ndarray, quad: np.ndarray) -> np.ndarray:
    top_left, top_right, bottom_right, bottom_left = quad

    width_a = np.linalg.norm(bottom_right - bottom_left)
    width_b = np.linalg.norm(top_right - top_left)
    max_width = int(max(width_a, width_b))

    height_a = np.linalg.norm(top_right - bottom_right)
    height_b = np.linalg.norm(top_left - bottom_left)
    max_height = int(max(height_a, height_b))

    max_width = max(max_width, 100)
    max_height = max(max_height, 100)

    destination = np.array(
        [[0, 0], [max_width - 1, 0], [max_width - 1, max_height - 1], [0, max_height - 1]],
        dtype=np.float32,
    )

    matrix = cv2.getPerspectiveTransform(quad, destination)
    return cv2.warpPerspective(image, matrix, (max_width, max_height), flags=cv2.INTER_LINEAR)


def _build_red_mask(image: np.ndarray, spec: ImageProcessingSpec) -> np.ndarray:
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

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

    return cv2.bitwise_or(mask_red_1, mask_red_2)


def _crop_to_grid(image: np.ndarray, red_mask: np.ndarray) -> tuple[np.ndarray, tuple[int, int, int, int]]:
    row_density = red_mask.mean(axis=1).astype(np.float32) / 255.0
    col_density = red_mask.mean(axis=0).astype(np.float32) / 255.0

    row_threshold = max(0.008, float(np.percentile(row_density, 75) * 0.35))
    col_threshold = max(0.008, float(np.percentile(col_density, 75) * 0.35))

    row_indices = np.where(row_density >= row_threshold)[0]
    col_indices = np.where(col_density >= col_threshold)[0]

    if row_indices.size == 0 or col_indices.size == 0:
        height, width = image.shape[:2]
        return image, (0, 0, width, height)

    y1 = int(row_indices[0])
    y2 = int(row_indices[-1])
    x1 = int(col_indices[0])
    x2 = int(col_indices[-1])

    margin_y = max(2, int((y2 - y1 + 1) * 0.01))
    margin_x = max(2, int((x2 - x1 + 1) * 0.01))

    y1 = max(0, y1 - margin_y)
    y2 = min(image.shape[0] - 1, y2 + margin_y)
    x1 = max(0, x1 - margin_x)
    x2 = min(image.shape[1] - 1, x2 + margin_x)

    cropped = image[y1 : y2 + 1, x1 : x2 + 1]

    # Prevent over-aggressive cropping when border grid is faint.
    height, width = image.shape[:2]
    cropped_h, cropped_w = cropped.shape[:2]
    if cropped_w < int(width * 0.80) or cropped_h < int(height * 0.70):
        return image, (0, 0, width, height)

    return cropped, (x1, y1, x2 + 1, y2 + 1)


def align_ctg_image(image: np.ndarray, spec: ImageProcessingSpec) -> AlignmentResult:
    if image.shape[0] > image.shape[1]:
        image = cv2.rotate(image, cv2.ROTATE_90_CLOCKWISE)

    skew_angle = _estimate_skew_angle(image, spec)
    rotated = _rotate_with_bounds(image, -skew_angle) if abs(skew_angle) >= 0.15 else image

    quad = _detect_perspective_quad(rotated, spec)
    perspective_applied = quad is not None
    rectified = _warp_from_quad(rotated, quad) if quad is not None else rotated

    # Keep original rotation-only result when perspective warp collapses aspect ratio.
    if rectified.shape[1] < rectified.shape[0]:
        rectified = rotated
        perspective_applied = False

    red_mask = _build_red_mask(rectified, spec)
    cropped, crop_bbox = _crop_to_grid(rectified, red_mask)

    if quad is None:
        height, width = rotated.shape[:2]
        quad = np.array(
            [[0, 0], [width - 1, 0], [width - 1, height - 1], [0, height - 1]],
            dtype=np.float32,
        )

    return AlignmentResult(
        aligned_image=cropped,
        skew_angle_degrees=float(skew_angle),
        perspective_applied=perspective_applied,
        crop_bbox=crop_bbox,
        perspective_corners=quad.tolist(),
    )
