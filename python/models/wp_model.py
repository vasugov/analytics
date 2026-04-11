#wp_model.py
#xgboost binary classifier for win probability
#predicts p(posteam wins) given game state; target = actual game outcome

from __future__ import annotations

import xgboost as xgb
from .base import NFLModel


# win probability uses additional score-context features beyond base epa features
WP_FEATURES = [
    "down", "ydstogo", "yardline_100",
    "score_differential",
    "half_seconds_remaining",
    "game_seconds_remaining",
    "posteam_timeouts_remaining",
    "defteam_timeouts_remaining",
    "is_two_minute", "is_final_two", "is_4th_quarter",
    "score_abs", "time_pressure", "score_x_time",
    "field_position_norm", "quarter_bucket",
]


class WPModel(NFLModel):
    """
    Predicts win probability (0-1) for the possession team at any game state.
    The target column must be 'posteam_won' (1 if posteam won the game, else 0).
    Calibration note: tree models are typically well-calibrated for this task;
    use CalibratedClassifierCV if brier score > 0.20 on the validation set.
    """

    name = "wp_model"
    task = "binary"

    def __init__(
        self,
        n_estimators: int = 500,
        max_depth: int = 5,
        learning_rate: float = 0.05,
        subsample: float = 0.8,
        colsample_bytree: float = 0.7,
        min_child_weight: int = 30,
        scale_pos_weight: float = 1.0,
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
            scale_pos_weight=scale_pos_weight,
            objective="binary:logistic",
            eval_metric="logloss",
            use_label_encoder=False,
            random_state=seed,
            n_jobs=-1,
            tree_method="hist",
        )
        self.feature_cols = WP_FEATURES

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
