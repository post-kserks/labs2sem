from __future__ import annotations

from pathlib import Path

import yaml

from internal.domain.models import AxisSpec, ImageProcessingSpec, OutputSpec, PipelineConfig, TimeSpec


def load_pipeline_config(config_path: Path) -> PipelineConfig:
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with config_path.open("r", encoding="utf-8") as config_file:
        data = yaml.safe_load(config_file) or {}

    image_data = data.get("image", {})
    time_data = data.get("time", {})
    axes_data = data.get("axes", {})
    output_data = data.get("output", {})

    upper_axis_data = axes_data.get("upper", {})
    lower_axis_data = axes_data.get("lower", {})

    upper_axis = AxisSpec(
        name=upper_axis_data.get("name", "upper_signal"),
        unit=upper_axis_data.get("unit", "a.u."),
        min_value=float(upper_axis_data.get("min_value", 0.0)),
        max_value=float(upper_axis_data.get("max_value", 1.0)),
    )
    lower_axis = AxisSpec(
        name=lower_axis_data.get("name", "lower_signal"),
        unit=lower_axis_data.get("unit", "a.u."),
        min_value=float(lower_axis_data.get("min_value", 0.0)),
        max_value=float(lower_axis_data.get("max_value", 1.0)),
    )

    time_spec = TimeSpec(
        duration_minutes=float(time_data.get("duration_minutes", 20.0)),
        start_timestamp=time_data.get("start_timestamp"),
        sampling_step_seconds=float(time_data.get("sampling_step_seconds", 1.0)),
    )

    image_spec = ImageProcessingSpec(
        dark_threshold=int(image_data.get("dark_threshold", 145)),
        max_tracking_jump_px=int(image_data.get("max_tracking_jump_px", 70)),
        smoothing_window=int(image_data.get("smoothing_window", 11)),
        min_line_length_ratio=float(image_data.get("min_line_length_ratio", 0.35)),
    )

    output_spec = OutputSpec(
        include_debug_images=bool(output_data.get("include_debug_images", True)),
    )

    return PipelineConfig(
        upper_axis=upper_axis,
        lower_axis=lower_axis,
        time_spec=time_spec,
        image_spec=image_spec,
        output_spec=output_spec,
    )
