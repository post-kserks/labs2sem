from __future__ import annotations

from dataclasses import replace
from pathlib import Path

import cv2

from internal.domain.models import PipelineConfig, ProcessingArtifacts
from pkg.ctg.aligner import align_ctg_image
from pkg.ctg.analyzer import analyze_ctg_layout
from pkg.ctg.digitizer import digitize_ctg
from pkg.ctg.extractor import separate_signal_from_grid, split_fhr_toco_masks
from pkg.ctg.quality import evaluate_quality
from pkg.ctg.reconstructor import reconstruct
from pkg.timeseries.exporter import save_ctg_csv, save_report, to_dataframe
from utils.files import ensure_directory


class ChartProcessingPipeline:
    def __init__(self, config: PipelineConfig) -> None:
        self._config = config

    def run(self, image_path: Path, output_dir: Path) -> ProcessingArtifacts:
        ensure_directory(output_dir)

        source = cv2.imread(str(image_path))
        if source is None:
            raise FileNotFoundError(f"Unable to read image: {image_path}")

        alignment = align_ctg_image(source, spec=self._config.image_spec)
        aligned = alignment.aligned_image

        metadata = analyze_ctg_layout(aligned, config=self._config)

        effective_time_spec = replace(self._config.time_spec, duration_minutes=metadata.duration_minutes)
        candidates: list[dict[str, object]] = []

        for mode in ("strict", "relaxed"):
            signal_mask, _, _, guidance_gray = separate_signal_from_grid(
                aligned,
                spec=self._config.image_spec,
                mode=mode,
            )
            fhr_mask, toco_mask = split_fhr_toco_masks(signal_mask, metadata, mode=mode)

            digitized = digitize_ctg(
                fhr_mask=fhr_mask,
                toco_mask=toco_mask,
                metadata=metadata,
                upper_axis=self._config.upper_axis,
                lower_axis=self._config.lower_axis,
                time_spec=effective_time_spec,
                image_spec=self._config.image_spec,
                guidance_gray=guidance_gray,
            )

            quality = evaluate_quality(
                fhr_mask=fhr_mask,
                toco_mask=toco_mask,
                fhr_track_y=digitized.fhr_track_y,
                toco_track_y=digitized.toco_track_y,
                fhr_values=digitized.fhr_values_native,
                toco_values=digitized.toco_values_native,
                quality_spec=self._config.quality_spec,
            )
            candidates.append(
                {
                    "mode": mode,
                    "signal_mask": signal_mask,
                    "fhr_mask": fhr_mask,
                    "toco_mask": toco_mask,
                    "digitized": digitized,
                    "quality": quality,
                }
            )

        passed = [item for item in candidates if item["quality"].passed]
        pool = passed if passed else candidates
        selected = max(pool, key=lambda item: item["quality"].overall_score)

        signal_mask = selected["signal_mask"]
        fhr_mask = selected["fhr_mask"]
        toco_mask = selected["toco_mask"]
        digitized = selected["digitized"]
        quality = selected["quality"]

        dataframe = to_dataframe(digitized.series)

        base = image_path.stem
        aligned_path = output_dir / f"{base}_aligned.jpg"
        fhr_panel_path = output_dir / f"{base}_fhr_panel.jpg"
        toco_panel_path = output_dir / f"{base}_toco_panel.jpg"
        signal_mask_path = output_dir / f"{base}_signal_mask.png"
        fhr_mask_path = output_dir / f"{base}_fhr_mask.png"
        toco_mask_path = output_dir / f"{base}_toco_mask.png"
        csv_path = output_dir / f"{base}_timeseries.csv"
        reconstructed_path = output_dir / f"{base}_reconstructed.png"
        report_path = output_dir / f"{base}_report.json"

        sep_top = max(1, min(aligned.shape[0] - 2, metadata.separator_y_top))
        sep_bottom = max(sep_top + 1, min(aligned.shape[0] - 1, metadata.separator_y_bottom))

        fhr_panel = aligned[:sep_top, :]
        toco_panel = aligned[sep_bottom:, :]

        if self._config.output_spec.include_debug_images:
            cv2.imwrite(str(aligned_path), aligned)
            cv2.imwrite(str(fhr_panel_path), fhr_panel)
            cv2.imwrite(str(toco_panel_path), toco_panel)
            cv2.imwrite(str(signal_mask_path), signal_mask)
            cv2.imwrite(str(fhr_mask_path), fhr_mask)
            cv2.imwrite(str(toco_mask_path), toco_mask)

        save_ctg_csv(path=csv_path, dataframe=dataframe, metadata=metadata, source_image=image_path)
        reconstruct(csv_path=csv_path, output_path=reconstructed_path)

        save_report(
            path=report_path,
            metadata=metadata,
            extra={
                "source_image": str(image_path),
                "aligned_shape": list(aligned.shape),
                "skew_angle_degrees": alignment.skew_angle_degrees,
                "perspective_applied": alignment.perspective_applied,
                "crop_bbox": list(alignment.crop_bbox),
                "perspective_corners": alignment.perspective_corners,
                "samples_count": int(len(dataframe)),
                "extraction_mode": selected["mode"],
                "quality": {
                    "fhr_coverage": quality.fhr_coverage,
                    "toco_coverage": quality.toco_coverage,
                    "fhr_mean_distance": quality.fhr_mean_distance,
                    "toco_mean_distance": quality.toco_mean_distance,
                    "fhr_jump_ratio": quality.fhr_jump_ratio,
                    "toco_jump_ratio": quality.toco_jump_ratio,
                    "overall_score": quality.overall_score,
                    "passed": quality.passed,
                },
            },
        )

        return ProcessingArtifacts(
            aligned_image_path=aligned_path,
            fhr_panel_path=fhr_panel_path,
            toco_panel_path=toco_panel_path,
            signal_mask_path=signal_mask_path,
            fhr_mask_path=fhr_mask_path,
            toco_mask_path=toco_mask_path,
            reconstructed_plot_path=reconstructed_path,
            csv_path=csv_path,
            report_path=report_path,
        )
