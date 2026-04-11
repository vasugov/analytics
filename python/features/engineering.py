#engineering.py
#all feature transformations for ml models
#input: raw play-level dataframe from play_features.csv
#output: enriched dataframe with binned, interaction, and situational features

import numpy as np
import pandas as pd


# ── numeric feature list used by all models ──────────────────────────────────
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
    # engineered
    "down_x_ydstogo",
    "yardline_x_down",
    "time_pressure",
    "ydstogo_clipped",
    "field_position_norm",
    "score_abs",
    "play_type_bin",
]


def add_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all engineered features to a play-level dataframe.
    Returns a new dataframe; does not mutate the input.
    """
    df = df.copy()

    # ── interaction terms ────────────────────────────────────────────────────
    df["down_x_ydstogo"]   = df["down"] * df["ydstogo"]
    df["yardline_x_down"]  = df["yardline_100"] * df["down"]
    df["score_x_time"]     = df["score_differential"] * (
        df["game_seconds_remaining"] / 3600.0
    )

    # ── clipped / normalised versions ────────────────────────────────────────
    df["ydstogo_clipped"]     = df["ydstogo"].clip(upper=20)
    df["field_position_norm"] = (100 - df["yardline_100"]) / 100.0  # 0 = own gl, 1 = opp gl
    df["score_abs"]           = df["score_differential"].abs()
    df["time_pressure"]       = df["score_abs"] / (
        df["game_seconds_remaining"] / 3600.0 + 0.01
    )

    # ── play type binary ─────────────────────────────────────────────────────
    df["play_type_bin"] = (df["play_type"] == "pass").astype(int)

    # ── categorical bins (kept as codes for tree models) ────────────────────
    df["ydstogo_bucket"] = pd.cut(
        df["ydstogo"],
        bins=[0, 3, 6, 10, 20, 100],
        labels=[0, 1, 2, 3, 4],
        include_lowest=True,
    ).astype(int)

    df["field_zone"] = pd.cut(
        df["yardline_100"],
        bins=[0, 10, 20, 40, 60, 80, 100],
        labels=[0, 1, 2, 3, 4, 5],
        include_lowest=True,
    ).astype(int)

    df["score_bucket"] = pd.cut(
        df["score_differential"],
        bins=[-100, -21, -14, -7, -3, 3, 7, 14, 21, 100],
        labels=[0, 1, 2, 3, 4, 5, 6, 7, 8],
        include_lowest=True,
    ).astype(int)

    df["quarter_bucket"] = pd.cut(
        df["game_seconds_remaining"],
        bins=[-1, 900, 1800, 2700, 3600],
        labels=[4, 3, 2, 1],
    ).astype(int)

    return df


def get_feature_cols() -> list[str]:
    """Return the full list of numeric feature columns after add_features()."""
    return BASE_FEATURES + [
        "ydstogo_bucket",
        "field_zone",
        "score_bucket",
        "quarter_bucket",
        "score_x_time",
        "yardline_x_down",
    ]


def time_split(df: pd.DataFrame, val_season: int = 2023):
    """
    Chronological train / validation split.
    Train on all seasons before val_season; validate on val_season.
    """
    train = df[df["season"] < val_season].copy()
    val   = df[df["season"] == val_season].copy()
    return train, val
