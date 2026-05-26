# CTG Tape Processor

Pipeline for processing photo-based CTG strips (кардиотокограмма):

1. Align strip by grid lines and correct perspective.
2. Detect separator band and split FHR/TOCO zones.
3. Calibrate time/value scales from red grid.
4. Extract dark signal lines while excluding red grid.
5. Digitize two time series (FHR and TOCO).
6. Save CTG CSV with metadata comments and reconstruct CTG image from CSV.

## Architecture

- `cmd/main.py` — CLI processing entrypoint.
- `cmd/render_from_csv.py` — reconstruct image from CSV.
- `internal/application/pipeline.py` — orchestration.
- `internal/domain/models.py` — domain contracts (`CTGMetadata`, `ExtractedSeries`, config specs).
- `internal/services/config_loader.py` — YAML config loader.
- `pkg/ctg/aligner.py` — skew + perspective correction + crop.
- `pkg/ctg/analyzer.py` — separator/grid analysis and metadata extraction.
- `pkg/ctg/extractor.py` — HSV masks for grid/signal and FHR-TOCO split.
- `pkg/ctg/digitizer.py` — column-wise digitization, interpolation, median smoothing.
- `pkg/ctg/reconstructor.py` — CTG-style PNG reconstruction from CSV.
- `pkg/timeseries/exporter.py` — CSV/report serialization.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Run

List images:

```bash
.venv/bin/python -m cmd.main --input-dir . --list
```

Process by explicit file:

```bash
.venv/bin/python -m cmd.main --image 13-2-3.jpg --output-dir output
```

Reconstruct from CSV:

```bash
.venv/bin/python -m cmd.render_from_csv --csv output/13-2-3_timeseries.csv --output output/13-2-3_from_csv.png
```

## CSV format

Generated CSV includes metadata comments:

```csv
# source: 13-2-3.jpg
# type: CTG
# time_start: 09:00
# duration_min: 20.000
# fhr_scale: 60-200 bpm
# toco_scale: 0-100
# paper_speed: 1.0 cm/min
# px_per_minute: 47.300
time_min,fhr_bpm,toco_units
0.000,138.2,4.1
...
```

## Notes

- `paper_speed` is estimated heuristically (1 vs 3 cm/min) from calibrated horizontal scale.
- `time_start` comes from config (`config/defaults.yaml`) unless OCR module is added.
