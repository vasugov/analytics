# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

NFL Analytics Framework — a research prototype that computes advanced football metrics (EPA, Success Rate, WPA, Red Zone Efficiency, Drive Efficiency) from historical play-by-play data via nflfastR, then visualizes results in Jupyter notebooks.

## Architecture

Three distinct layers:

1. **R pipeline** (`R/`) — data ingestion, metric computation, and feature export. `R/pipeline/run_pipeline.R` orchestrates: load play-by-play via nflfastR → compute 5 aggregate metrics → export play-level ML features → write all CSVs to `data/outputs/`. Each metric + the feature extractor live in `R/metrics/`.

2. **Python ML layer** (`python/`) — gradient boosting models trained on play-level features.
   - `python/features/engineering.py` — all feature transforms (bins, interactions, situational flags).
   - `python/models/` — 5 XGBoost models: `EPAModel` (regression), `WPModel`, `SuccessModel`, `RZModel`, `DriveModel` (multiclass). All inherit `NFLModel` base class.
   - `python/training/trainer.py` — training orchestration with time-based CV (2021–22 train / 2023 val).
   - `python/export/json_exporter.py` — converts outputs + model reports to `web/data/*.json` for the static web page.
   - `python/api/main.py` — full FastAPI with metrics, team profile, `/predict/play`, and feature importance endpoints.

3. **Web page** (`web/nfl.html`) — self-contained static page for `vasugov/dinkybeat.github.io`. Loads `./data/metrics.json`; falls back to inline sample data. Sections: League Rankings, Team Profile, EPA Model, Play Predictor.

Data flow:
```
nflfastR → R pipeline → data/outputs/*.csv
                               │
                    ┌──────────┴──────────┐
              aggregate CSVs        play_features.csv
              (existing metrics)    (new ML dataset)
                    │                     │
            Python loader.py      python/training/trainer.py
            FastAPI /metrics/      → models/saved/*.pkl
                    │                     │
                    └──────────┬──────────┘
                        json_exporter.py
                               │
                         web/data/*.json
                               │
                         web/nfl.html (GitHub Pages)
```

## Common Commands

### R Pipeline

```r
# Run full pipeline (from R or RScript)
source("R/pipeline/run_pipeline.R")

# Or from the shell
Rscript R/pipeline/run_pipeline.R
```

### Python — Full Pipeline

```bash
# Install dependencies
pip install -r requirements.txt

# Train all gradient boosting models (requires play_features.csv from R)
python -m python.training.trainer --model all
# or train one model:  --model epa | wp | success | rz | drive

# Export outputs to web/data/ for GitHub Pages deployment
python -m python.export.json_exporter

# Start API (full endpoints)
uvicorn python.api.main:app --reload

# Training notebooks (in order)
jupyter notebook notebooks/models/01_epa_model.ipynb
jupyter notebook notebooks/models/02_wp_model.ipynb
jupyter notebook notebooks/models/03_team_rankings.ipynb

# Visualization notebook (original)
jupyter notebook notebooks/looks/metrics1.ipynb
```

### Web Deployment (GitHub Pages)

Copy `web/nfl.html` and `web/data/` to `vasugov/dinkybeat.github.io`:
```
dinkybeat.github.io/nfl.html
dinkybeat.github.io/data/metrics.json
dinkybeat.github.io/data/prediction_grid.json
```
The page works immediately with inline sample data even before the pipeline is run.

### Binder (no local setup needed)
The repo includes a Binder badge in README.md — open the notebook in-browser without installing anything.

## Configuration

`config/settings.yaml` controls which seasons to process (`pipeline.seasons`), season type (`REG`/`POST`/`ALL`), enabled metrics, and path roots. The R pipeline reads this config; update it to change scope.

## Data

- `data/raw/` — raw nflfastR RDS/CSV files (gitignored)
- `data/processed/` — intermediate data (gitignored)
- `data/outputs/` — final metric CSVs (committed); 5 aggregate files + `play_features.csv` (play-level ML dataset, ~250k rows, gitignored)
- `models/saved/` — trained XGBoost model `.pkl` files (gitignored)
- `models/reports/` — per-model JSON training reports (train/val metrics, feature importance)
- `web/data/` — JSON exports for GitHub Pages (`metrics.json`, `prediction_grid.json`)

## Key Conventions

- R metrics follow a consistent pattern: each file exports one `compute_<metric>(pbp)` function that takes a play-by-play dataframe and returns a summarized dataframe. New metrics should follow this pattern and be registered in `run_pipeline.R`.
- `R/utils/helpers.R` provides `filter_regular_season()` and `save_output()` — use these instead of reimplementing.
- Python paths resolve relative to package root via `Path(__file__).resolve().parents[n]`; follow this pattern to stay portable.
- All Python ML models inherit `NFLModel` from `python/models/base.py` — use `fit_with_eval()` (with early stopping) rather than bare `fit()`.
- Feature engineering is centralised in `python/features/engineering.py`. `add_features()` returns a new dataframe; never mutate in place. `get_feature_cols()` returns the canonical feature list.
- Training uses time-based CV only (not random k-fold) — train on 2021–2022, validate on 2023.
- After training, run `json_exporter.py` to push results to `web/data/`. The web page reads from there.
