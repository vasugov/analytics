#epa_model.py
#xgboost regression model that predicts expected points added (epa) per play
#trained on play-level game-state features; ground truth epa from nflfastR

from __future__ import annotations

import xgboost as xgb
from .base import NFLModel
from python.features.engineering import get_feature_cols


class EPAModel(NFLModel):
    """
    Predicts EPA (continuous) given game-state features.
    This is the core metric model — all other derived rankings use residuals
    from this model to measure over/under-performance vs. expectation.
    """

    name = "epa_model"
    task = "regression"

    def __init__(
        self,
        n_estimators: int = 600,
        max_depth: int = 6,
        learning_rate: float = 0.05,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        min_child_weight: int = 20,
        reg_alpha: float = 0.1,
        reg_lambda: float = 1.0,
        seed: int = 42,
    ) -> None:
        super().__init__()
        self.model = xgb.XGBRegressor(
            n_estimators=n_estimators,
            max_depth=max_depth,
            learning_rate=learning_rate,
            subsample=subsample,
            colsample_bytree=colsample_bytree,
            min_child_weight=min_child_weight,
            reg_alpha=reg_alpha,
            reg_lambda=reg_lambda,
            random_state=seed,
            n_jobs=-1,
            tree_method="hist",
            eval_metric="rmse",
        )
        self.feature_cols = get_feature_cols()

    def fit_with_eval(self, X_train, y_train, X_val, y_val):
        """Fit with early stopping on the validation set."""
        self.feature_cols = list(X_train.columns)
        self.model.set_params(early_stopping_rounds=50)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=100,
        )
        self.is_fitted = True
        return self
