# NFL Analytics

NFL play-by-play analytics using nflfastR and XGBoost. Computes advanced metrics from 2021-2023 seasons and trains gradient boosting models on play-level features.

[![Try it out at govardha.net](https://govardha.net/olave)

## metrics

- EPA (expected points added per play)
- success rate (fraction of plays with EPA > 0)
- WPA (win probability added)
- red zone efficiency (TD rate inside opp 20)
- drive efficiency (scoring rate + avg EPA per drive)

## how to run

```bash
bash scripts/install.sh
Rscript R/pipeline/run_pipeline.R
python3 -m python.training.trainer --model all
python3 -m python.export.json_exporter
uvicorn python.api.main:app --reload
```

or all at once: `bash scripts/run_all.sh`

## models

trained on 2021-22, validated on 2023

| model | val metric |
|---|---|
| EPA regression | RMSE 1.384, R² 0.010 |
| play success | AUC 0.614, Brier 0.235 |
| red zone TD | AUC 0.766, Brier 0.132 |
| win probability | binary classifier |
| drive outcome | multiclass classifier |

## notebooks

- `notebooks/looks/metrics1.ipynb` - metric visualizations
- `notebooks/models/01_epa_model.ipynb` - EPA model + SHAP
- `notebooks/models/02_wp_model.ipynb` - win probability + calibration
- `notebooks/models/03_team_rankings.ipynb` - composite rankings

## web

copy `web/nfl.html` and `web/data/` to your GitHub Pages repo. works with inline sample data out of the box.

## structure

```
R/          data ingestion and metric computation
python/     models, training, api, export
notebooks/  analysis
web/        static dashboard
data/       pipeline outputs
models/     saved models and reports
```
