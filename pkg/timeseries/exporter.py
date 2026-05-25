from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import cv2
import numpy as np
import pandas as pd

from internal.domain.models import AxisSpec, ExtractedSeries, TimeSpec


def _sanitize_column_name(name: str) -> str:
    return name.strip().lower().replace(" ", "_")


def to_dataframe(series: ExtractedSeries, upper_axis: AxisSpec, lower_axis: AxisSpec, time_spec: TimeSpec) -> pd.DataFrame:
    upper_col = f"{_sanitize_column_name(upper_axis.name)}_{_sanitize_column_name(upper_axis.unit)}"
    lower_col = f"{_sanitize_column_name(lower_axis.name)}_{_sanitize_column_name(lower_axis.unit)}"

    dataframe = pd.DataFrame(
        {
            "time_seconds": series.time_seconds,
            "time_minutes": series.time_seconds / 60.0,
            upper_col: series.upper_values,
            lower_col: series.lower_values,
        }
    )

    if time_spec.start_timestamp:
        try:
            start = datetime.strptime(time_spec.start_timestamp, "%H:%M")
            dataframe["clock_time"] = [
                (start + timedelta(seconds=float(seconds))).strftime("%H:%M:%S")
                for seconds in series.time_seconds
            ]
        except ValueError:
            pass

    return dataframe


def save_csv(dataframe: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    dataframe.to_csv(path, index=False)


def _to_plot_points(
    x_values: np.ndarray,
    y_values: np.ndarray,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
    left: int,
    top: int,
    width: int,
    height: int,
) -> np.ndarray:
    x_norm = (x_values - x_min) / max(1e-6, x_max - x_min)
    y_norm = (y_values - y_min) / max(1e-6, y_max - y_min)

    x_px = left + (x_norm * width)
    y_px = top + height - (y_norm * height)

    points = np.stack([x_px, y_px], axis=1)
    points = np.nan_to_num(points, nan=0.0, posinf=0.0, neginf=0.0)
    return points.astype(np.int32)


def _draw_plot_area(canvas: np.ndarray, left: int, top: int, width: int, height: int, title: str, y_label: str) -> None:
    cv2.rectangle(canvas, (left, top), (left + width, top + height), (220, 220, 220), 1)
    cv2.putText(canvas, title, (left, top - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (30, 30, 30), 1, cv2.LINE_AA)
    cv2.putText(canvas, y_label, (left + 8, top + 22), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (50, 50, 50), 1, cv2.LINE_AA)


def _draw_grid(canvas: np.ndarray, left: int, top: int, width: int, height: int, x_ticks: int = 10, y_ticks: int = 8) -> None:
    for i in range(1, x_ticks):
        x = left + int(i * width / x_ticks)
        cv2.line(canvas, (x, top), (x, top + height), (240, 240, 240), 1)
    for i in range(1, y_ticks):
        y = top + int(i * height / y_ticks)
        cv2.line(canvas, (left, y), (left + width, y), (240, 240, 240), 1)


def save_plot(
    dataframe: pd.DataFrame,
    path: Path,
    upper_axis: AxisSpec,
    lower_axis: AxisSpec,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)

    upper_col = f"{_sanitize_column_name(upper_axis.name)}_{_sanitize_column_name(upper_axis.unit)}"
    lower_col = f"{_sanitize_column_name(lower_axis.name)}_{_sanitize_column_name(lower_axis.unit)}"

    x_values = dataframe["time_minutes"].to_numpy(dtype=np.float32)
    upper_values = dataframe[upper_col].to_numpy(dtype=np.float32)
    lower_values = dataframe[lower_col].to_numpy(dtype=np.float32)

    canvas_height = 900
    canvas_width = 1600
    canvas = np.full((canvas_height, canvas_width, 3), 255, dtype=np.uint8)

    margin_left = 95
    margin_right = 40
    margin_top = 60
    margin_bottom = 60
    gap = 60

    plot_width = canvas_width - margin_left - margin_right
    plot_height = (canvas_height - margin_top - margin_bottom - gap) // 2

    top_plot_top = margin_top
    bottom_plot_top = margin_top + plot_height + gap

    _draw_grid(canvas, margin_left, top_plot_top, plot_width, plot_height)
    _draw_plot_area(
        canvas,
        margin_left,
        top_plot_top,
        plot_width,
        plot_height,
        title="Extracted Graph 1",
        y_label=f"{upper_axis.name} ({upper_axis.unit})",
    )

    _draw_grid(canvas, margin_left, bottom_plot_top, plot_width, plot_height)
    _draw_plot_area(
        canvas,
        margin_left,
        bottom_plot_top,
        plot_width,
        plot_height,
        title="Extracted Graph 2",
        y_label=f"{lower_axis.name} ({lower_axis.unit})",
    )

    x_min = float(np.min(x_values))
    x_max = float(np.max(x_values))

    upper_points = _to_plot_points(
        x_values,
        upper_values,
        x_min,
        x_max,
        upper_axis.min_value,
        upper_axis.max_value,
        margin_left,
        top_plot_top,
        plot_width,
        plot_height,
    )
    lower_points = _to_plot_points(
        x_values,
        lower_values,
        x_min,
        x_max,
        lower_axis.min_value,
        lower_axis.max_value,
        margin_left,
        bottom_plot_top,
        plot_width,
        plot_height,
    )

    cv2.polylines(canvas, [upper_points.reshape(-1, 1, 2)], False, (20, 20, 20), 2, cv2.LINE_AA)
    cv2.polylines(canvas, [lower_points.reshape(-1, 1, 2)], False, (20, 20, 20), 2, cv2.LINE_AA)

    x_label = "Time (minutes)"
    cv2.putText(
        canvas,
        x_label,
        (canvas_width // 2 - 70, canvas_height - 20),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (30, 30, 30),
        2,
        cv2.LINE_AA,
    )

    cv2.imwrite(str(path), canvas)
