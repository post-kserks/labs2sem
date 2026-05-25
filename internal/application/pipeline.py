from __future__ import annotations

import json
from pathlib import Path

import cv2

from internal.domain.models import PipelineConfig, ProcessingArtifacts
from pkg.imageproc.alignment import align_chart_image
from pkg.imageproc.chart_splitter import split_into_panels
from pkg.imageproc.curve_extractor import extract_curve
from pkg.timeseries.exporter import save_csv, save_plot, to_dataframe
from pkg.timeseries.series_builder import build_extracted_series
from utils.files import ensure_directory


class ChartProcessingPipeline:
    def __init__(self, config: PipelineConfig) -> None:
        self._config = config

    def run(self, image_path: Path, output_dir: Path) -> ProcessingArtifacts:
        ensure_directory(output_dir)

        image = cv2.imread(str(image_path))
        if image is None:
            raise FileNotFoundError(f"Unable to read image: {image_path}")

        aligned_image, skew_angle = align_chart_image(
            image,
            min_line_length_ratio=self._config.image_spec.min_line_length_ratio,
        )

        upper_panel, lower_panel, separator_row = split_into_panels(aligned_image)

        upper_curve_y, upper_mask = extract_curve(
            panel=upper_panel,
            dark_threshold=self._config.image_spec.dark_threshold,
            max_jump_px=self._config.image_spec.max_tracking_jump_px,
            smoothing_window=self._config.image_spec.smoothing_window,
            row_start_ratio=0.05,
            row_end_ratio=0.92,
        )
        lower_curve_y, lower_mask = extract_curve(
            panel=lower_panel,
            dark_threshold=self._config.image_spec.dark_threshold,
            max_jump_px=self._config.image_spec.max_tracking_jump_px,
            smoothing_window=self._config.image_spec.smoothing_window,
            row_start_ratio=0.05,
            row_end_ratio=0.98,
        )

        series = build_extracted_series(
            upper_y_pixels=upper_curve_y,
            lower_y_pixels=lower_curve_y,
            upper_panel_height=upper_panel.shape[0],
            lower_panel_height=lower_panel.shape[0],
            upper_axis=self._config.upper_axis,
            lower_axis=self._config.lower_axis,
            time_spec=self._config.time_spec,
        )

        dataframe = to_dataframe(
            series=series,
            upper_axis=self._config.upper_axis,
            lower_axis=self._config.lower_axis,
            time_spec=self._config.time_spec,
        )

        base_name = image_path.stem
        aligned_path = output_dir / f"{base_name}_aligned.jpg"
        upper_path = output_dir / f"{base_name}_upper_panel.jpg"
        lower_path = output_dir / f"{base_name}_lower_panel.jpg"
        upper_mask_path = output_dir / f"{base_name}_upper_mask.png"
        lower_mask_path = output_dir / f"{base_name}_lower_mask.png"
        csv_path = output_dir / f"{base_name}_timeseries.csv"
        plot_path = output_dir / f"{base_name}_reconstructed_plot.png"
        report_path = output_dir / f"{base_name}_report.json"

        cv2.imwrite(str(aligned_path), aligned_image)
        cv2.imwrite(str(upper_path), upper_panel)
        cv2.imwrite(str(lower_path), lower_panel)
        cv2.imwrite(str(upper_mask_path), upper_mask)
        cv2.imwrite(str(lower_mask_path), lower_mask)

        save_csv(dataframe, csv_path)
        save_plot(
            dataframe=dataframe,
            path=plot_path,
            upper_axis=self._config.upper_axis,
            lower_axis=self._config.lower_axis,
        )

        self._save_report(
            path=report_path,
            image_path=image_path,
            separator_row=separator_row,
            skew_angle=skew_angle,
            upper_panel_shape=upper_panel.shape,
            lower_panel_shape=lower_panel.shape,
            points_count=len(dataframe),
        )

        return ProcessingArtifacts(
            aligned_image_path=aligned_path,
            upper_panel_path=upper_path,
            lower_panel_path=lower_path,
            extracted_mask_upper_path=upper_mask_path,
            extracted_mask_lower_path=lower_mask_path,
            plot_path=plot_path,
            csv_path=csv_path,
            report_path=report_path,
        )

    def _save_report(
        self,
        path: Path,
        image_path: Path,
        separator_row: int,
        skew_angle: float,
        upper_panel_shape: tuple[int, ...],
        lower_panel_shape: tuple[int, ...],
        points_count: int,
    ) -> None:
        report = {
            "source_image": str(image_path),
            "skew_angle_degrees": round(skew_angle, 4),
            "separator_row": separator_row,
            "upper_panel_shape": upper_panel_shape,
            "lower_panel_shape": lower_panel_shape,
            "duration_minutes": self._config.time_spec.duration_minutes,
            "sampling_step_seconds": self._config.time_spec.sampling_step_seconds,
            "graph_1_axis": {
                "name": self._config.upper_axis.name,
                "unit": self._config.upper_axis.unit,
                "min": self._config.upper_axis.min_value,
                "max": self._config.upper_axis.max_value,
            },
            "graph_2_axis": {
                "name": self._config.lower_axis.name,
                "unit": self._config.lower_axis.unit,
                "min": self._config.lower_axis.min_value,
                "max": self._config.lower_axis.max_value,
            },
            "timeseries_points": points_count,
        }

        with path.open("w", encoding="utf-8") as file:
            json.dump(report, file, ensure_ascii=False, indent=2)
