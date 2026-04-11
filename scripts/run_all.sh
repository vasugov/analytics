#!/usr/bin/env bash
# run_all.sh — full pipeline: R data → train models → export web data
set -e
cd "$(dirname "$0")/.."

echo "========================================"
echo "  NFL Analytics — full pipeline"
echo "========================================"

echo ""
echo "--> step 1/4  install dependencies"
bash scripts/install.sh

echo ""
echo "--> step 2/4  R pipeline (ingest + metrics + play features)"
if command -v Rscript &>/dev/null; then
  Rscript R/pipeline/run_pipeline.R
else
  echo "   R not found — skipping (using existing CSVs)"
fi

echo ""
echo "--> step 3/4  train gradient boosting models"
python3 -m python.training.trainer --model all

echo ""
echo "--> step 4/4  export web data"
python3 -m python.export.json_exporter

echo ""
echo "========================================"
echo "  done."
echo "  copy web/ to vasugov/dinkybeat.github.io"
echo "========================================"
