from __future__ import annotations

from pathlib import Path

import yaml

from internal.domain.models import AxisSpec, ImageProcessingSpec, OutputSpec, PipelineConfig, QualitySpec, TimeSpec


def _to_int(data: dict, key: str, default: int) -> int:
    return int(data.get(key, default))


def _to_float(data: dict, key: str, default: float) -> float:
    return float(data.get(key, default))


def load_pipeline_config(config_path: Path) -> PipelineConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as config_file:
        data = yaml.safe_load(config_file) or {}

    image_data = data.get("image", {})
    time_data = data.get("time", {})
    axes_data = data.get("axes", {})
    output_data = data.get("output", {})
    quality_data = data.get("quality", {})

    upper_axis_data = axes_data.get("upper", {})
    lower_axis_data = axes_data.get("lower", {})

    upper_axis = AxisSpec(
        name=upper_axis_data.get("name", "fhr"),
        unit=upper_axis_data.get("unit", "bpm"),
        min_value=_to_float(upper_axis_data, "min_value", 60.0),
        max_value=_to_float(upper_axis_data, "max_value", 200.0),
        major_step=_to_float(upper_axis_data, "major_step", 20.0),
    )

    lower_axis = AxisSpec(
        name=lower_axis_data.get("name", "toco"),
        unit=lower_axis_data.get("unit", "units"),
        min_value=_to_float(lower_axis_data, "min_value", 0.0),
        max_value=_to_float(lower_axis_data, "max_value", 100.0),
        major_step=_to_float(lower_axis_data, "major_step", 20.0),
    )

    time_spec = TimeSpec(
        duration_minutes=_to_float(time_data, "duration_minutes", 20.0),
        start_timestamp=time_data.get("start_timestamp"),
        sampling_step_seconds=_to_float(time_data, "sampling_step_seconds", 1.0),
    )

    image_spec = ImageProcessingSpec(
        canny_low=_to_int(image_data, "canny_low", 60),
        canny_high=_to_int(image_data, "canny_high", 180),
        min_line_length_ratio=_to_float(image_data, "min_line_length_ratio", 0.4),
        perspective_min_area_ratio=_to_float(image_data, "perspective_min_area_ratio", 0.5),
        clahe_clip_limit=_to_float(image_data, "clahe_clip_limit", 2.0),
        clahe_tile_size=_to_int(image_data, "clahe_tile_size", 8),
        red_hue_low_1=_to_int(image_data, "red_hue_low_1", 0),
        red_hue_high_1=_to_int(image_data, "red_hue_high_1", 15),
        red_hue_low_2=_to_int(image_data, "red_hue_low_2", 165),
        red_hue_high_2=_to_int(image_data, "red_hue_high_2", 180),
        red_s_min=_to_int(image_data, "red_s_min", 80),
        red_v_min=_to_int(image_data, "red_v_min", 80),
        dark_v_max=_to_int(image_data, "dark_v_max", 120),
        max_tracking_jump_px=_to_int(image_data, "max_tracking_jump_px", 75),
        interpolate_limit=_to_int(image_data, "interpolate_limit", 10),
        median_filter_window=_to_int(image_data, "median_filter_window", 5),
    )

    output_spec = OutputSpec(
        include_debug_images=bool(output_data.get("include_debug_images", True)),
    )
    quality_spec = QualitySpec(
        min_coverage=float(quality_data.get("min_coverage", 0.20)),
        max_mean_distance=float(quality_data.get("max_mean_distance", 3.0)),
        max_jump_ratio=float(quality_data.get("max_jump_ratio", 0.12)),
        min_score=float(quality_data.get("min_score", 0.45)),
    )

    return PipelineConfig(
        upper_axis=upper_axis,
        lower_axis=lower_axis,
        time_spec=time_spec,
        image_spec=image_spec,
        output_spec=output_spec,
        quality_spec=quality_spec,
    )
