#rz_model.py
#red zone touchdown probability model
#trained only on plays where yardline_100 <= 20

from __future__ import annotations

import xgboost as xgb
from .base import NFLModel

RZ_FEATURES = [
    "down", "ydstogo", "yardline_100",
    "score_differential",
    "half_seconds_remaining",
    "game_seconds_remaining",
    "posteam_timeouts_remaining",
    "defteam_timeouts_remaining",
    "is_two_minute", "is_4th_quarter",
    "is_goal_to_go",
    "shotgun_flag", "no_huddle_flag",
    "down_x_ydstogo",
    "field_position_norm",
    "score_abs",
    "play_type_bin",
]


class RZModel(NFLModel):
    #filter input data to yardline_100 <= 20 before fitting

    name = "rz_model"
    task = "binary"

    def __init__(
        self,
        n_estimators: int = 400,
        max_depth: int = 4,
        learning_rate: float = 0.07,
        subsample: float = 0.85,
        colsample_bytree: float = 0.8,
        min_child_weight: int = 15,
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
            eval_metric="auc",
            random_state=seed,
            n_jobs=-1,
            tree_method="hist",
        )
        self.feature_cols = RZ_FEATURES

    def fit_with_eval(self, X_train, y_train, X_val, y_val):
        if hasattr(X_train, "columns"):
            self.feature_cols = list(X_train.columns)
        X_tr, X_v = self._np(X_train), self._np(X_val)
        self.model.set_params(early_stopping_rounds=30)
        self.model.fit(
            X_tr, self._np(y_train),
            eval_set=[(X_v, self._np(y_val))],
            verbose=50,
        )
        self.is_fitted = True
        return self
