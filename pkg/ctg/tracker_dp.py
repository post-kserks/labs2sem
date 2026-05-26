from __future__ import annotations

import cv2
import numpy as np


def track_curve_dp(
    mask: np.ndarray,
    band_top: int,
    band_bottom: int,
    max_step_px: int,
    smooth_weight: float = 0.28,
    dark_weight: float = 0.05,
    gray_image: np.ndarray | None = None,
) -> np.ndarray:
    height, width = mask.shape
    band_top = max(0, min(height - 1, band_top))
    band_bottom = max(band_top + 1, min(height, band_bottom))

    band_h = band_bottom - band_top
    band_mask = mask[band_top:band_bottom, :]

    inv = cv2.bitwise_not(band_mask)
    dist = cv2.distanceTransform(inv, cv2.DIST_L2, 3).astype(np.float32)

    data_cost = dist
    if gray_image is not None:
        gray_band = gray_image[band_top:band_bottom, :].astype(np.float32) / 255.0
        data_cost = data_cost + (dark_weight * gray_band)

    # Softly bias toward rows where mask is present to reduce drift when there are gaps.
    support = (band_mask > 0).astype(np.float32)
    row_support = cv2.GaussianBlur(support.mean(axis=1).reshape(-1, 1), (1, 7), 0).reshape(-1)
    row_bias = 1.0 - row_support
    data_cost = data_cost + row_bias[:, None]

    max_step = max(1, int(max_step_px))
    inf = np.float32(1e9)

    dp_prev = np.full(band_h, inf, dtype=np.float32)
    back_ptr = np.zeros((width, band_h), dtype=np.int16)

    dp_prev[:] = data_cost[:, 0]

    step_offsets = np.arange(-max_step, max_step + 1, dtype=np.int16)

    for x in range(1, width):
        dp_curr = np.full(band_h, inf, dtype=np.float32)
        for y in range(band_h):
            best_cost = inf
            best_prev = y
            for offset in step_offsets:
                yp = y + int(offset)
                if yp < 0 or yp >= band_h:
                    continue
                transition = smooth_weight * abs(float(offset))
                cost = dp_prev[yp] + transition
                if cost < best_cost:
                    best_cost = cost
                    best_prev = yp

            dp_curr[y] = best_cost + data_cost[y, x]
            back_ptr[x, y] = np.int16(best_prev)

        dp_prev = dp_curr

    end_y = int(np.argmin(dp_prev))
    track = np.zeros(width, dtype=np.float32)
    track[-1] = float(end_y + band_top)

    y = end_y
    for x in range(width - 1, 0, -1):
        y = int(back_ptr[x, y])
        track[x - 1] = float(y + band_top)

    return track
