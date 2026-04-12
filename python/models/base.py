#base.py
#nflmodel base class: shared fit / predict / save / load interface

from __future__ import annotations

from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_error,
    r2_score,
    roc_auc_score,
    brier_score_loss,
    log_loss,
)

MODELS_DIR = Path(__file__).resolve().parents[2] / "models" / "saved"


class NFLModel:
    #abstract base for all gradient-boosting nfl models
    #subclasses set self.model and self.task in __init__
    #task: 'regression' | 'binary' | 'multiclass'

    name: str = "base"
    task: str = "regression"

    def __init__(self) -> None:
        self.model = None
        self.feature_cols: list[str] = []
        self.is_fitted: bool = False

    @staticmethod
    def _np(X):
        #coerce dataframe/series to numpy; pass arrays through (xgboost 3.x + pandas 1.x compat)
        return X.to_numpy() if hasattr(X, "to_numpy") else X

    def fit(self, X_train: pd.DataFrame, y_train: pd.Series, **kwargs) -> "NFLModel":
        self.feature_cols = list(X_train.columns)
        self.model.fit(X_train, y_train, **kwargs)
        self.is_fitted = True
        return self

    def predict(self, X: pd.DataFrame) -> np.ndarray:
        self._check_fitted()
        if hasattr(X, "columns"):
            X = X[self.feature_cols].to_numpy()
        return self.model.predict(X)

    def predict_proba(self, X: pd.DataFrame) -> np.ndarray:
        #only valid for classification tasks
        self._check_fitted()
        if hasattr(X, "columns"):
            X = X[self.feature_cols].to_numpy()
        if self.task == "binary":
            return self.model.predict_proba(X)[:, 1]
        return self.model.predict_proba(X)

    def evaluate(self, X: pd.DataFrame, y: pd.Series) -> dict:
        preds = self.predict(X)
        if self.task == "regression":
            rmse = np.sqrt(mean_squared_error(y, preds))
            return {
                "rmse": round(rmse, 4),
                "mae":  round(mean_absolute_error(y, preds), 4),
                "r2":   round(r2_score(y, preds), 4),
            }
        if self.task == "binary":
            proba = self.predict_proba(X)
            return {
                "auc":    round(roc_auc_score(y, proba), 4),
                "brier":  round(brier_score_loss(y, proba), 4),
                "logloss": round(log_loss(y, proba), 4),
            }
        return {"accuracy": round((preds == y).mean(), 4)}

    def save(self, path: Path | None = None) -> Path:
        self._check_fitted()
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        out = path or MODELS_DIR / f"{self.name}.pkl"
        joblib.dump(self, out)
        return out

    @classmethod
    def load(cls, path: Path | None = None) -> "NFLModel":
        MODELS_DIR.mkdir(parents=True, exist_ok=True)
        p = path or MODELS_DIR / f"{cls.name}.pkl"
        return joblib.load(p)

    def _check_fitted(self) -> None:
        if not self.is_fitted:
            raise RuntimeError(f"{self.__class__.__name__} has not been fitted yet.")
