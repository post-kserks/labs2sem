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


@dataclass(frozen=True)
class TimeSpec:
    duration_minutes: float
    start_timestamp: str | None
    sampling_step_seconds: float


@dataclass(frozen=True)
class ImageProcessingSpec:
    dark_threshold: int
    max_tracking_jump_px: int
    smoothing_window: int
    min_line_length_ratio: float


@dataclass(frozen=True)
class OutputSpec:
    include_debug_images: bool


@dataclass(frozen=True)
class PipelineConfig:
    upper_axis: AxisSpec
    lower_axis: AxisSpec
    time_spec: TimeSpec
    image_spec: ImageProcessingSpec
    output_spec: OutputSpec


@dataclass
class ExtractedSeries:
    time_seconds: np.ndarray
    upper_values: np.ndarray
    lower_values: np.ndarray


@dataclass
class ProcessingArtifacts:
    aligned_image_path: Path
    upper_panel_path: Path
    lower_panel_path: Path
    extracted_mask_upper_path: Path
    extracted_mask_lower_path: Path
    plot_path: Path
    csv_path: Path
    report_path: Path
