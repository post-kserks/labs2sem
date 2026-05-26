from __future__ import annotations

import numpy as np

from internal.domain.models import QualitySpec, SeriesQuality


def _coverage(mask: np.ndarray) -> float:
    cols_with_signal = np.count_nonzero(mask.sum(axis=0) > 0)
    return float(cols_with_signal) / max(1.0, float(mask.shape[1]))


def _jump_ratio(series: np.ndarray, jump_threshold: float) -> float:
    if len(series) < 2:
        return 1.0
    diffs = np.abs(np.diff(series.astype(np.float32)))
    return float(np.mean(diffs > jump_threshold))


def _mean_distance_to_mask(track_y: np.ndarray, mask: np.ndarray) -> float:
    inv = 255 - mask
    dist = np.asarray(inv, dtype=np.uint8)
    dist = np.where(dist > 0, 255, 0).astype(np.uint8)

    import cv2

    dmap = cv2.distanceTransform(dist, cv2.DIST_L2, 3)

    xs = np.arange(mask.shape[1])
    ys = np.clip(np.rint(track_y).astype(np.int32), 0, mask.shape[0] - 1)
    sampled = dmap[ys, xs]
    return float(np.mean(sampled))


def evaluate_quality(
    fhr_mask: np.ndarray,
    toco_mask: np.ndarray,
    fhr_track_y: np.ndarray,
    toco_track_y: np.ndarray,
    fhr_values: np.ndarray,
    toco_values: np.ndarray,
    quality_spec: QualitySpec,
) -> SeriesQuality:
    fhr_cov = _coverage(fhr_mask)
    toco_cov = _coverage(toco_mask)

    fhr_dist = _mean_distance_to_mask(fhr_track_y, fhr_mask)
    toco_dist = _mean_distance_to_mask(toco_track_y, toco_mask)

    fhr_jump = _jump_ratio(fhr_values, jump_threshold=8.0)
    toco_jump = _jump_ratio(toco_values, jump_threshold=10.0)

    coverage_score = min(1.0, (0.5 * (fhr_cov + toco_cov)) / max(1e-6, quality_spec.min_coverage))
    dist_score = min(1.0, quality_spec.max_mean_distance / max(1e-6, 0.5 * (fhr_dist + toco_dist)))
    jump_score = min(1.0, quality_spec.max_jump_ratio / max(1e-6, 0.5 * (fhr_jump + toco_jump)))

    overall = 0.45 * coverage_score + 0.35 * dist_score + 0.20 * jump_score

    passed = (
        fhr_cov >= quality_spec.min_coverage
        and toco_cov >= quality_spec.min_coverage
        and fhr_dist <= quality_spec.max_mean_distance
        and toco_dist <= quality_spec.max_mean_distance
        and fhr_jump <= quality_spec.max_jump_ratio
        and toco_jump <= quality_spec.max_jump_ratio
        and overall >= quality_spec.min_score
    )

    return SeriesQuality(
        fhr_coverage=fhr_cov,
        toco_coverage=toco_cov,
        fhr_mean_distance=fhr_dist,
        toco_mean_distance=toco_dist,
        fhr_jump_ratio=fhr_jump,
        toco_jump_ratio=toco_jump,
        overall_score=float(overall),
        passed=bool(passed),
    )
