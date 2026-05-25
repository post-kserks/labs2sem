from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from internal.domain.models import AxisSpec
from pkg.timeseries.exporter import save_plot


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render chart image from extracted CSV time series.")
    parser.add_argument("--csv", type=Path, required=True, help="Path to CSV produced by pipeline.")
    parser.add_argument("--output", type=Path, required=True, help="Output PNG path.")
    parser.add_argument("--upper-name", type=str, default="fetal_heart_rate")
    parser.add_argument("--upper-unit", type=str, default="bpm")
    parser.add_argument("--upper-min", type=float, default=50.0)
    parser.add_argument("--upper-max", type=float, default=210.0)
    parser.add_argument("--lower-name", type=str, default="uterine_activity")
    parser.add_argument("--lower-unit", type=str, default="mmHg")
    parser.add_argument("--lower-min", type=float, default=0.0)
    parser.add_argument("--lower-max", type=float, default=100.0)
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if not args.csv.exists():
        raise FileNotFoundError(f"CSV not found: {args.csv}")

    dataframe = pd.read_csv(args.csv)

    upper_axis = AxisSpec(
        name=args.upper_name,
        unit=args.upper_unit,
        min_value=args.upper_min,
        max_value=args.upper_max,
    )
    lower_axis = AxisSpec(
        name=args.lower_name,
        unit=args.lower_unit,
        min_value=args.lower_min,
        max_value=args.lower_max,
    )

    save_plot(dataframe=dataframe, path=args.output, upper_axis=upper_axis, lower_axis=lower_axis)
    print(f"Rendered: {args.output}")


if __name__ == "__main__":
    main()
