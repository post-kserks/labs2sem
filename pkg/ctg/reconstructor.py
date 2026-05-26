from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import cv2
import numpy as np
import pandas as pd


def read_metadata(csv_path: Path) -> dict[str, str]:
    metadata: dict[str, str] = {}
    with csv_path.open("r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if not line.startswith("#"):
                break
            payload = line[1:].strip()
            if ":" not in payload:
                continue
            key, value = payload.split(":", 1)
            metadata[key.strip()] = value.strip()
    return metadata


def _draw_grid(
    canvas: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    x_minor_step: float,
    x_major_step: float,
    y_minor_step: float,
    y_major_step: float,
    x_min: float,
    x_max: float,
    y_min: float,
    y_max: float,
) -> None:
    width = max(1, x2 - x1)
    height = max(1, y2 - y1)

    def to_x(value: float) -> int:
        ratio = (value - x_min) / max(1e-6, x_max - x_min)
        return int(round(x1 + ratio * width))

    def to_y(value: float) -> int:
        ratio = (value - y_min) / max(1e-6, y_max - y_min)
        return int(round(y2 - ratio * height))

    x = x_min
    while x <= x_max + 1e-6:
        px = to_x(x)
        is_major = abs((x - x_min) / max(x_major_step, 1e-6) - round((x - x_min) / max(x_major_step, 1e-6))) < 1e-4
        color = (80, 80, 210) if is_major else (140, 140, 230)
        thickness = 1 if is_major else 1
        cv2.line(canvas, (px, y1), (px, y2), color, thickness)
        x += x_minor_step

    y = y_min
    while y <= y_max + 1e-6:
        py = to_y(y)
        is_major = abs((y - y_min) / max(y_major_step, 1e-6) - round((y - y_min) / max(y_major_step, 1e-6))) < 1e-4
        color = (80, 80, 210) if is_major else (140, 140, 230)
        cv2.line(canvas, (x1, py), (x2, py), color, 1)
        y += y_minor_step

    cv2.rectangle(canvas, (x1, y1), (x2, y2), (70, 70, 180), 1)


def _draw_series(
    canvas: np.ndarray,
    x1: int,
    y1: int,
    x2: int,
    y2: int,
    time_values: np.ndarray,
    signal_values: np.ndarray,
    time_min: float,
    time_max: float,
    value_min: float,
    value_max: float,
) -> None:
    width = max(1, x2 - x1)
    height = max(1, y2 - y1)

    time_ratio = (time_values - time_min) / max(1e-6, time_max - time_min)
    value_ratio = (signal_values - value_min) / max(1e-6, value_max - value_min)

    px = x1 + (time_ratio * width)
    py = y2 - (value_ratio * height)

    points = np.stack([px, py], axis=1)
    points = np.nan_to_num(points, nan=0.0, posinf=0.0, neginf=0.0).astype(np.int32)
    cv2.polylines(canvas, [points.reshape(-1, 1, 2)], False, (20, 20, 20), 2, cv2.LINE_AA)


def reconstruct(csv_path: Path, output_path: Path | None = None) -> Path:
    if output_path is None:
        output_path = csv_path.with_name(f"{csv_path.stem}_reconstructed.png")

    metadata = read_metadata(csv_path)
    dataframe = pd.read_csv(csv_path, comment="#")

    time = dataframe["time_min"].to_numpy(dtype=np.float32)
    fhr = dataframe["fhr_bpm"].to_numpy(dtype=np.float32)
    toco = dataframe["toco_units"].to_numpy(dtype=np.float32)

    duration = float(metadata.get("duration_min", time[-1] if len(time) > 0 else 0.0))

    canvas_h, canvas_w = 900, 1600
    canvas = np.full((canvas_h, canvas_w, 3), (245, 245, 255), dtype=np.uint8)

    left = 90
    right = canvas_w - 35
    top = 50
    bottom = canvas_h - 55
    gap = 55

    upper_h = int((bottom - top - gap) * 0.64)
    lower_h = (bottom - top - gap) - upper_h

    u_y1 = top
    u_y2 = u_y1 + upper_h
    l_y1 = u_y2 + gap
    l_y2 = l_y1 + lower_h

    _draw_grid(
        canvas,
        left,
        u_y1,
        right,
        u_y2,
        x_minor_step=0.2,
        x_major_step=1.0,
        y_minor_step=10.0,
        y_major_step=20.0,
        x_min=0.0,
        x_max=max(duration, 0.1),
        y_min=60.0,
        y_max=200.0,
    )
    _draw_grid(
        canvas,
        left,
        l_y1,
        right,
        l_y2,
        x_minor_step=0.2,
        x_major_step=1.0,
        y_minor_step=10.0,
        y_major_step=20.0,
        x_min=0.0,
        x_max=max(duration, 0.1),
        y_min=0.0,
        y_max=100.0,
    )

    _draw_series(
        canvas,
        left,
        u_y1,
        right,
        u_y2,
        time,
        fhr,
        0.0,
        max(duration, 0.1),
        60.0,
        200.0,
    )
    _draw_series(
        canvas,
        left,
        l_y1,
        right,
        l_y2,
        time,
        toco,
        0.0,
        max(duration, 0.1),
        0.0,
        100.0,
    )

    cv2.putText(canvas, "FHR (bpm)", (left + 8, u_y1 + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (30, 30, 30), 2, cv2.LINE_AA)
    cv2.putText(canvas, "TOCO", (left + 8, l_y1 + 24), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (30, 30, 30), 2, cv2.LINE_AA)
    cv2.putText(canvas, "Time (min)", (canvas_w // 2 - 65, canvas_h - 18), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (30, 30, 30), 2, cv2.LINE_AA)

    start_label = metadata.get("time_start")
    if start_label:
        try:
            start_dt = datetime.strptime(start_label, "%H:%M")
            mark = 0
            while mark <= int(duration):
                dt = start_dt + timedelta(minutes=mark)
                x = int(round(left + (mark / max(duration, 0.1)) * (right - left)))
                if mark % 10 == 0:
                    cv2.putText(
                        canvas,
                        dt.strftime("%H:%M"),
                        (x - 24, u_y2 + 34),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.5,
                        (35, 35, 35),
                        1,
                        cv2.LINE_AA,
                    )
                mark += 1
        except ValueError:
            pass

    output_path.parent.mkdir(parents=True, exist_ok=True)
    cv2.imwrite(str(output_path), canvas)
    return output_path
