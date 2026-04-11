#drive_model.py
#predicts drive outcome (touchdown / field_goal / punt / turnover / other)
#multiclass xgboost classifier trained on first-play-of-drive features

from __future__ import annotations

import numpy as np
import xgboost as xgb
from .base import NFLModel

DRIVE_FEATURES = [
    "down", "ydstogo", "yardline_100",
    "score_differential",
    "half_seconds_remaining",
    "game_seconds_remaining",
    "posteam_timeouts_remaining",
    "defteam_timeouts_remaining",
    "is_two_minute", "is_4th_quarter",
    "field_position_norm",
    "score_abs", "time_pressure",
    "quarter_bucket",
]

DRIVE_CLASSES = ["touchdown", "field_goal", "punt", "turnover", "other"]


class DriveModel(NFLModel):
    """
    Multi-class classifier for drive outcome prediction.
    Input: features of the first play (or drive-start state) of a drive.
    Output: probability distribution over DRIVE_CLASSES.

    To prepare data: group by (game_id, drive), take the first row per drive,
    and map fixed_drive_result to integer class labels using DRIVE_CLASSES.
    """

    name = "drive_model"
    task = "multiclass"

    CLASSES = DRIVE_CLASSES

    def __init__(
        self,
        n_estimators: int = 400,
        max_depth: int = 5,
        learning_rate: float = 0.06,
        subsample: float = 0.8,
        colsample_bytree: float = 0.8,
        min_child_weight: int = 20,
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
            objective="multi:softprob",
            num_class=len(DRIVE_CLASSES),
            eval_metric="mlogloss",
            use_label_encoder=False,
            random_state=seed,
            n_jobs=-1,
            tree_method="hist",
        )
        self.feature_cols = DRIVE_FEATURES

    def predict_proba_named(self, X) -> dict[str, np.ndarray]:
        """Returns dict of class_name -> probability array."""
        proba = self.model.predict_proba(X[self.feature_cols])
        return {cls: proba[:, i] for i, cls in enumerate(DRIVE_CLASSES)}

    def fit_with_eval(self, X_train, y_train, X_val, y_val):
        self.feature_cols = list(X_train.columns)
        self.model.set_params(early_stopping_rounds=40)
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_val, y_val)],
            verbose=50,
        )
        self.is_fitted = True
        return self
