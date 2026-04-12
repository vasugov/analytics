#success_model.py
#predicts p(play success) where success = epa > 0
#binary xgboost classifier

from __future__ import annotations

import xgboost as xgb
from .base import NFLModel
from python.features.engineering import get_feature_cols


class SuccessModel(NFLModel):
    name = "success_model"
    task = "binary"

    def __init__(
        self,
        n_estimators: int = 500,
        max_depth: int = 5,
        learning_rate: float = 0.06,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        min_child_weight: int = 25,
        seed: int = 42,
    ) -> None:
        super().__init__()
        self.model = xgb.XGBClassifier(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            min_child_weight=min_child_weight,
            objective="binary:logistic",
            eval_metric="logloss",
            random_state=seed,
            n_jobs=-1,
            tree_method="hist",
        )
        self.feature_cols = get_feature_cols()

    def fit_with_eval(self, X_train, y_train, X_val, y_val):
        if hasattr(X_train, "columns"):
            self.feature_cols = list(X_train.columns)
        X_tr, X_v = self._np(X_train), self._np(X_val)
        self.model.set_params(early_stopping_rounds=40)
        self.model.fit(
            X_tr, self._np(y_train),
            eval_set=[(X_v, self._np(y_val))],
            verbose=50,
        )
        self.is_fitted = True
        return self
