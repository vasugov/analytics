# NFL Analytics — Gradient Boosting Framework

[![Launch in Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/vasugov/analytics/main?labpath=notebooks%2Flooks%2Fmetrics1.ipynb)

A research framework for computing and modelling advanced NFL metrics from play-by-play data.
The system uses an R ingestion pipeline (nflfastR) feeding into XGBoost gradient boosting models
trained on 101,000+ plays across the 2021–2023 regular seasons.

---

## What it does

| Layer | What happens |
|---|---|
| **R pipeline** | Loads nflfastR play-by-play → computes 5 aggregate metrics → exports play-level feature dataset |
| **Feature engineering** | 27 game-state features: down, distance, field position, score differential, time, situational flags, interaction terms |
| **XGBoost models** | EPA regression · Play success · Red zone TD probability · Win probability · Drive outcome |
| **FastAPI** | Serves metrics and live play predictions at `/predict/play` |
| **Web page** | Static dashboard (`web/nfl.html`) — league rankings, team profiles, feature importance, play predictor |

---

## Metrics

- **Expected Points Added (EPA)** — average points contributed per offensive play
- **Success Rate** — fraction of plays with EPA > 0
- **Win Probability Added (WPA)** — total WP impact accumulated by each team
- **Red Zone Efficiency** — TD rate on plays inside the opponent's 20
- **Drive Efficiency** — scoring rate and average EPA per drive

---

## Running the full pipeline

### 1. Install dependencies
```bash
bash scripts/install.sh
```

### 2. R pipeline — generates all CSVs including play-level ML dataset
```bash
Rscript R/pipeline/run_pipeline.R
```

### 3. Train gradient boosting models
```bash
python3 -m python.training.trainer --model all
# or train one model: --model epa | success | rz | wp | drive
```

### 4. Export web data
```bash
python3 -m python.export.json_exporter
```

### 5. Start API
```bash
uvicorn python.api.main:app --reload
```

### One-shot (all steps)
```bash
bash scripts/run_all.sh
```

---

## Notebooks

| Notebook | Purpose |
|---|---|
| `notebooks/looks/metrics1.ipynb` | Plotly visualizations of all 5 aggregate metrics |
| `notebooks/models/01_epa_model.ipynb` | Train EPA model, SHAP analysis, team residuals |
| `notebooks/models/02_wp_model.ipynb` | Win probability model + calibration curve |
| `notebooks/models/03_team_rankings.ipynb` | Model-derived composite team rankings + JSON export |

Run in the browser via the Binder badge — no local setup needed.

---

## Model results (2021–22 train / 2023 validation)

| Model | Task | Val metric |
|---|---|---|
| EPA | Regression | RMSE 1.384, R² 0.010 |
| Success | Binary classification | AUC 0.614, Brier 0.235 |
| Red Zone TD | Binary classification | AUC 0.766, Brier 0.132 |

*Note: play-level EPA is inherently noisy — individual outcomes are nearly unpredictable from game state alone.
The low R² reflects this variance floor, not model failure. Team-level aggregate predictions are much more stable.*

---

## Web deployment

Copy `web/nfl.html` and `web/data/` to `vasugov/dinkybeat.github.io`:

```
nfl.html
data/
  metrics.json
  prediction_grid.json
```

The page works immediately with inline sample data. Place real `metrics.json` alongside it to show live model outputs.

---

## Project structure

```
R/
  ingestion/load_pbp.R          load nflfastR play-by-play
  metrics/                      compute_epa, compute_success_rate, etc.
  pipeline/run_pipeline.R       full orchestration
  utils/helpers.R               filter_regular_season, save_output

python/
  features/engineering.py       all feature transforms
  models/                       NFLModel base + 5 XGBoost models
  training/trainer.py           training orchestration, time-based CV
  export/json_exporter.py       write web/data/*.json
  api/main.py                   FastAPI endpoints
  pipeline/loader.py            read data/outputs CSVs

notebooks/
  looks/metrics1.ipynb          descriptive charts
  models/                       training + analysis notebooks

web/
  nfl.html                      standalone dashboard page
  data/                         JSON outputs for GitHub Pages

data/outputs/                   committed metric CSVs
models/reports/                 training metrics + feature importance JSON
config/settings.yaml            seasons, paths, enabled metrics
```
