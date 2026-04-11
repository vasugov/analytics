# Web Deployment

Copy `nfl.html` and the `data/` folder to your GitHub Pages repo:

```
vasugov/dinkybeat.github.io/
  nfl.html          ← the page (or nfl/index.html for /nfl/ URL)
  data/
    metrics.json
    prediction_grid.json
```

The page loads `./data/metrics.json` automatically.
If not found, it falls back to inline sample data so it always works.

## Updating with real model data

1. Run the R pipeline to generate play_features.csv:
   ```
   Rscript R/pipeline/run_pipeline.R
   ```

2. Train all gradient boosting models:
   ```
   python -m python.training.trainer --model all
   ```

3. Export to JSON:
   ```
   python -m python.export.json_exporter
   ```

4. Copy `web/data/` to your GitHub Pages repo and push.
