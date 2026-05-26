from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

from internal.domain.models import CTGMetadata, ExtractedSeries


def to_dataframe(series: ExtractedSeries) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "time_min": series.time_min,
            "fhr_bpm": series.fhr_bpm,
            "toco_units": series.toco_units,
        }
    )


def save_ctg_csv(path: Path, dataframe: pd.DataFrame, metadata: CTGMetadata, source_image: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    header_lines = [
        f"# source: {source_image.name}",
        "# type: CTG",
        f"# time_start: {metadata.time_start if metadata.time_start else 'unknown'}",
        f"# duration_min: {metadata.duration_minutes:.3f}",
        "# fhr_scale: 60-200 bpm",
        "# toco_scale: 0-100",
        f"# paper_speed: {metadata.paper_speed_cm_per_min:.1f} cm/min",
        f"# px_per_minute: {metadata.px_per_minute:.3f}",
    ]

    with path.open("w", encoding="utf-8") as file:
        for line in header_lines:
            file.write(f"{line}\n")
        dataframe.to_csv(file, index=False)


def save_report(path: Path, metadata: CTGMetadata, extra: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    payload = {
        "metadata": {
            "px_per_minute": metadata.px_per_minute,
            "px_per_unit_fhr": metadata.px_per_unit_fhr,
            "px_per_unit_toco": metadata.px_per_unit_toco,
            "fhr_y_min": metadata.fhr_y_min,
            "fhr_y_max": metadata.fhr_y_max,
            "toco_y_min": metadata.toco_y_min,
            "toco_y_max": metadata.toco_y_max,
            "separator_y_top": metadata.separator_y_top,
            "separator_y_bottom": metadata.separator_y_bottom,
            "time_start": metadata.time_start,
            "duration_minutes": metadata.duration_minutes,
            "paper_speed_cm_per_min": metadata.paper_speed_cm_per_min,
        },
        "extra": extra,
    }

    with path.open("w", encoding="utf-8") as file:
        json.dump(payload, file, ensure_ascii=False, indent=2)
