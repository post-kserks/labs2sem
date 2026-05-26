from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np


@dataclass(frozen=True)
class AxisSpec:
    name: str
    unit: str
    min_value: float
    max_value: float
    major_step: float


@dataclass(frozen=True)
class TimeSpec:
    duration_minutes: float
    start_timestamp: str | None
    sampling_step_seconds: float


@dataclass(frozen=True)
class ImageProcessingSpec:
    canny_low: int
    canny_high: int
    min_line_length_ratio: float
    perspective_min_area_ratio: float
    clahe_clip_limit: float
    clahe_tile_size: int
    red_hue_low_1: int
    red_hue_high_1: int
    red_hue_low_2: int
    red_hue_high_2: int
    red_s_min: int
    red_v_min: int
    dark_v_max: int
    max_tracking_jump_px: int
    interpolate_limit: int
    median_filter_window: int


@dataclass(frozen=True)
class OutputSpec:
    include_debug_images: bool


@dataclass(frozen=True)
class QualitySpec:
    min_coverage: float
    max_mean_distance: float
    max_jump_ratio: float
    min_score: float


@dataclass(frozen=True)
class PipelineConfig:
    upper_axis: AxisSpec
    lower_axis: AxisSpec
    time_spec: TimeSpec
    image_spec: ImageProcessingSpec
    output_spec: OutputSpec
    quality_spec: QualitySpec


@dataclass(frozen=True)
class AlignmentResult:
    aligned_image: np.ndarray
    skew_angle_degrees: float
    perspective_applied: bool
    crop_bbox: tuple[int, int, int, int]
    perspective_corners: list[list[float]]


@dataclass(frozen=True)
class CTGMetadata:
    px_per_minute: float
    px_per_unit_fhr: float
    px_per_unit_toco: float
    fhr_y_min: int
    fhr_y_max: int
    toco_y_min: int
    toco_y_max: int
    separator_y_top: int
    separator_y_bottom: int
    time_start: str | None
    duration_minutes: float
    paper_speed_cm_per_min: float


@dataclass
class ExtractedSeries:
    time_min: np.ndarray
    fhr_bpm: np.ndarray
    toco_units: np.ndarray


@dataclass
class SeriesQuality:
    fhr_coverage: float
    toco_coverage: float
    fhr_mean_distance: float
    toco_mean_distance: float
    fhr_jump_ratio: float
    toco_jump_ratio: float
    overall_score: float
    passed: bool


@dataclass
class DigitizationResult:
    series: ExtractedSeries
    fhr_track_y: np.ndarray
    toco_track_y: np.ndarray
    fhr_values_native: np.ndarray
    toco_values_native: np.ndarray


@dataclass
class ProcessingArtifacts:
    aligned_image_path: Path
    fhr_panel_path: Path
    toco_panel_path: Path
    signal_mask_path: Path
    fhr_mask_path: Path
    toco_mask_path: Path
    reconstructed_plot_path: Path
    csv_path: Path
    report_path: Path
