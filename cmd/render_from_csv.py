from __future__ import annotations

import argparse
from pathlib import Path

from pkg.ctg.reconstructor import reconstruct


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Reconstruct CTG image from CSV with metadata header.")
    parser.add_argument("--csv", type=Path, required=True, help="Path to CTG CSV.")
    parser.add_argument("--output", type=Path, required=True, help="Output PNG path.")
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    if not args.csv.exists():
        raise FileNotFoundError(f"CSV not found: {args.csv}")

    output = reconstruct(csv_path=args.csv, output_path=args.output)
    print(f"Rendered: {output}")


if __name__ == "__main__":
    main()
