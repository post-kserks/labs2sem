# Medical Chart Processor

Production-oriented pipeline for extracting two time series from medical chart images (e.g., CTG-like scans):

1. Align image by horizontal/vertical grid lines.
2. Detect study duration and axis dimensionality from config (with report output).
3. Extract first graph (upper panel).
4. Extract second graph (lower panel).
5. Build synchronized time series.
6. Save `CSV` and reconstructed chart image.

## Architecture

- `cmd/` CLI entrypoint.
- `internal/application/` orchestration use-case (`ChartProcessingPipeline`).
- `internal/domain/` domain models/config contracts.
- `internal/services/` infrastructure service adapters (config loader).
- `pkg/imageproc/` computer vision primitives (alignment, panel split, curve extraction).
- `pkg/timeseries/` calibration, resampling, CSV and plot export.
- `utils/` cross-cutting helpers.
- `tests/` unit tests.

## Setup

```bash
python3 -m venv .venv
.venv/bin/pip install -e .
```

## Run

List input images:

```bash
.venv/bin/python -m cmd.main --input-dir . --list
```

Process first image from list:

```bash
.venv/bin/python -m cmd.main --input-dir . --index 1 --output-dir output
```

Process explicit image with overridden duration:

```bash
.venv/bin/python -m cmd.main --image 13-2-3.jpg --duration-minutes 20 --sampling-step 1 --output-dir output
```

Render image from an already prepared CSV:

```bash
.venv/bin/python -m cmd.render_from_csv --csv output/13-2-3_timeseries.csv --output output/13-2-3_from_csv.png
```

## Output

- `*_timeseries.csv` extracted numerical time series.
- `*_reconstructed_plot.png` reconstructed chart from CSV.
- `*_report.json` processing report with axis dimensionality and study duration.
- `*_aligned.jpg`, `*_upper_panel.jpg`, `*_lower_panel.jpg`, masks for debugging.

## Configuration

Edit `config/defaults.yaml`:

- `time.duration_minutes`: expected duration of study on full image width.
- `axes.upper` and `axes.lower`: dimensionality (`name`, `unit`, `min_value`, `max_value`).
- `image.dark_threshold`, `max_tracking_jump_px`, `smoothing_window`: extraction robustness.
