#engineering.py
#all feature transformations for ml models
#input: raw play-level dataframe from play_features.csv
#output: enriched dataframe with binned, interaction, and situational features

import numpy as np
import pandas as pd


#numeric feature list used by all models
BASE_FEATURES = [
    "down",
    "ydstogo",
    "yardline_100",
    "score_differential",
    "half_seconds_remaining",
    "game_seconds_remaining",
    "posteam_timeouts_remaining",
    "defteam_timeouts_remaining",
    "is_two_minute",
    "is_final_two",
    "is_4th_quarter",
    "is_red_zone",
    "is_goal_to_go",
    "shotgun_flag",
    "no_huddle_flag",
    #engineered
    "down_x_ydstogo",
    "yardline_x_down",
    "time_pressure",
    "ydstogo_clipped",
    "field_position_norm",
    "score_abs",
    "play_type_bin",
]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    #adds all engineered features; returns new dataframe without mutating input
    df = df.copy()

    #interaction terms
    df["down_x_ydstogo"]   = df["down"] * df["ydstogo"]
    df["yardline_x_down"]  = df["yardline_100"] * df["down"]
    df["score_x_time"]     = df["score_differential"] * (
        df["game_seconds_remaining"] / 3600.0
    )

    #clipped / normalised versions
    df["ydstogo_clipped"]     = df["ydstogo"].clip(upper=20)
    df["field_position_norm"] = (100 - df["yardline_100"]) / 100.0  #0=own gl, 1=opp gl
    df["score_abs"]           = df["score_differential"].abs()
    df["time_pressure"]       = df["score_abs"] / (
        df["game_seconds_remaining"] / 3600.0 + 0.01
    )

    #play type binary
    df["play_type_bin"] = (df["play_type"] == "pass").astype(int)

    #bucket features — np.digitize avoids pandas Categorical dtype
    #(pd.cut with labels produces Categorical which xgboost QuantileDMatrix rejects)
    df["ydstogo_bucket"] = np.digitize(
        df["ydstogo"].clip(0, 100).to_numpy(), bins=[4, 7, 11, 21]
    ).astype(np.int64)
    #0=1-3, 1=4-6, 2=7-10, 3=11-20, 4=21+

    df["field_zone"] = np.digitize(
        df["yardline_100"].clip(0, 100).to_numpy(), bins=[11, 21, 41, 61, 81]
    ).astype(np.int64)
    #0=goal_line, 1=red_zone, 2=scoring, 3=midfield, 4=own, 5=deep_own

    df["score_bucket"] = np.digitize(
        df["score_differential"].clip(-100, 100).to_numpy(),
        bins=[-21, -14, -7, -3, 3, 7, 14, 21],
    ).astype(np.int64)

    df["quarter_bucket"] = np.digitize(
        df["game_seconds_remaining"].clip(0, 3600).to_numpy(), bins=[901, 1801, 2701]
    ).astype(np.int64)
    #0=4th quarter, 1=3rd, 2=2nd, 3=1st

    return df


def get_feature_cols() -> list[str]:
    #full list of numeric feature columns after add_features()
    return BASE_FEATURES + [
        "ydstogo_bucket",
        "field_zone",
        "score_bucket",
        "quarter_bucket",
        "score_x_time",
        #note: yardline_x_down already in BASE_FEATURES
    ]


def time_split(df: pd.DataFrame, val_season: int = 2023):
    #chronological train/val split; train on seasons < val_season
    train = df[df["season"] < val_season].copy()
    val   = df[df["season"] == val_season].copy()
    return train, val
