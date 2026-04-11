#selection.py
#feature importance utilities and shap-based selection helpers

from __future__ import annotations

import numpy as np
import pandas as pd


def top_features(model, feature_names: list[str], n: int = 20) -> pd.DataFrame:
    """
    Return a dataframe of feature importances sorted descending.
    Works with any sklearn-compatible model that exposes feature_importances_.
    """
    importances = model.feature_importances_
    idx = np.argsort(importances)[::-1][:n]
    return pd.DataFrame(
        {
            "feature":    [feature_names[i] for i in idx],
            "importance": importances[idx],
        }
    )


def shap_summary(shap_values: np.ndarray, feature_names: list[str]) -> pd.DataFrame:
    """
    Compute mean absolute SHAP value per feature and return sorted dataframe.
    shap_values: array of shape (n_samples, n_features)
    """
    mean_abs = np.abs(shap_values).mean(axis=0)
    idx = np.argsort(mean_abs)[::-1]
    return pd.DataFrame(
        {
            "feature":        [feature_names[i] for i in idx],
            "mean_abs_shap":  mean_abs[idx],
        }
    )
