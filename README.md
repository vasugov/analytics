# OLAVE-NFl
## Operational Longitudinal Analytics Validation Engine for the NFL

NFL play-by-play analytics using nflfastR and XGBoost. Computes advanced metrics from 2021-2023 seasons and trains gradient boosting models on play-level features.

[Try it out at govardha.net](https://govardha.net/olave)

## Metrics

- EPA (expected points added per play)
- success rate (fraction of plays with EPA > 0)
- WPA (win probability added)
- red zone efficiency (TD rate inside opp 20)
- drive efficiency (scoring rate + avg EPA per drive)

## Run it:

```bash
bash scripts/install.sh
Rscript R/pipeline/run_pipeline.R
python3 -m python.training.trainer --model all
python3 -m python.export.json_exporter
uvicorn python.api.main:app --reload
```

## Models

trained on 2021-22, validated on 2023

| model | val metric |
|---|---|
| EPA regression | RMSE 1.384, R² 0.010 |
| play success | AUC 0.614, Brier 0.235 |
| red zone TD | AUC 0.766, Brier 0.132 |
| win probability | binary classifier |
| drive outcome | multiclass classifier |


