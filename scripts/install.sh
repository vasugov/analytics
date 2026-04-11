#!/usr/bin/env bash
# install.sh — install all python and R dependencies for nfl analytics
set -e

echo "==> python dependencies"
pip3 install \
  pandas numpy scipy matplotlib seaborn plotly \
  xgboost lightgbm scikit-learn shap optuna joblib \
  fastapi "uvicorn[standard]" pyyaml ipykernel

echo ""
echo "==> R dependencies (requires R to be installed)"
if command -v Rscript &>/dev/null; then
  Rscript -e "pkgs <- c('nflfastR','dplyr','readr'); \
    missing <- pkgs[!sapply(pkgs, requireNamespace, quietly=TRUE)]; \
    if (length(missing)) install.packages(missing, repos='https://cran.rstudio.com/')"
  echo "   R packages ok"
else
  echo "   R not found — skip R deps (not needed if play_features.csv already exists)"
fi

echo ""
echo "==> all done"
