from __future__ import annotations

import argparse
from dataclasses import replace
from pathlib import Path

from internal.application.pipeline import ChartProcessingPipeline
from internal.services.config_loader import load_pipeline_config
from utils.files import list_images


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="CTG processor: align photo, digitize FHR/TOCO, save CSV and reconstruction.",
    )
    parser.add_argument("--input-dir", type=Path, default=Path("."), help="Directory with source images.")
    parser.add_argument("--image", type=Path, default=None, help="Direct path to source image.")
    parser.add_argument("--index", type=int, default=None, help="1-based index from file list in input-dir.")
    parser.add_argument("--list", action="store_true", help="List available images and exit.")
    parser.add_argument("--config", type=Path, default=Path("config/defaults.yaml"), help="Path to YAML config.")
    parser.add_argument("--output-dir", type=Path, default=Path("output"), help="Output directory.")
    parser.add_argument("--duration-minutes", type=float, default=None, help="Override study duration in minutes.")
    parser.add_argument("--start-time", type=str, default=None, help="Optional start HH:MM for clock_time column.")
    parser.add_argument("--sampling-step", type=float, default=None, help="Resampling step in seconds.")
    return parser.parse_args()


def _resolve_image_path(args: argparse.Namespace) -> Path:
    if args.image is not None:
        if not args.image.exists():
            raise FileNotFoundError(f"Image path does not exist: {args.image}")
        return args.image

    input_dir = args.input_dir
    if not input_dir.exists() or not input_dir.is_dir():
        raise FileNotFoundError(f"Input directory is not available: {input_dir}")

    images = list_images(input_dir)

    if args.list:
        if not images:
            print("No supported images found.")
            return Path()

        for idx, path in enumerate(images, start=1):
            print(f"{idx}. {path.name}")
        return Path()

    if not images:
        raise FileNotFoundError("No supported image files found in input directory.")

    if args.index is not None:
        if args.index < 1 or args.index > len(images):
            raise IndexError(f"Image index out of range. Allowed: 1..{len(images)}")
        return images[args.index - 1]

    return images[0]


def main() -> None:
    args = _parse_args()

    selected_image = _resolve_image_path(args)
    if args.list:
        return

    config = load_pipeline_config(args.config)

    if args.duration_minutes is not None:
        config = replace(
            config,
            time_spec=replace(config.time_spec, duration_minutes=float(args.duration_minutes)),
        )
    if args.start_time is not None:
        config = replace(
            config,
            time_spec=replace(config.time_spec, start_timestamp=args.start_time),
        )
    if args.sampling_step is not None:
        config = replace(
            config,
            time_spec=replace(config.time_spec, sampling_step_seconds=float(args.sampling_step)),
        )

    pipeline = ChartProcessingPipeline(config=config)
    artifacts = pipeline.run(selected_image, args.output_dir)

    print(f"Selected image: {selected_image}")
    print(f"CSV: {artifacts.csv_path}")
    print(f"Plot: {artifacts.reconstructed_plot_path}")
    print(f"Report: {artifacts.report_path}")


if __name__ == "__main__":
    main()
