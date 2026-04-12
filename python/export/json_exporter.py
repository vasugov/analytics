#json_exporter.py
#converts all pipeline outputs + trained model reports into web-ready json
#run after the R pipeline and model training are complete
#usage: python -m python.export.json_exporter

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd

OUTPUTS_DIR = Path(__file__).resolve().parents[2] / "data" / "outputs"
REPORTS_DIR = Path(__file__).resolve().parents[2] / "models" / "reports"
WEB_DIR     = Path(__file__).resolve().parents[2] / "web" / "data"


def _read_csv(name: str) -> pd.DataFrame:
    return pd.read_csv(OUTPUTS_DIR / name)


def _load_report(name: str) -> dict:
    path = REPORTS_DIR / f"{name}.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def _clean(df: pd.DataFrame) -> list[dict]:
    return json.loads(df.to_json(orient="records"))


def build_composite_rankings(
    epa: pd.DataFrame,
    sr: pd.DataFrame,
    wpa: pd.DataFrame,
    rz: pd.DataFrame,
    drive: pd.DataFrame,
) -> list[dict]:
    #merges all metrics, ranks each col, computes composite score
    #lower composite = better (average of per-metric ranks)
    merged = (
        epa[["season", "posteam", "epa_per_play"]]
        .merge(sr[["season", "posteam", "success_rate"]], on=["season", "posteam"], how="inner")
        .merge(wpa[["season", "posteam", "total_wpa"]],  on=["season", "posteam"], how="inner")
        .merge(rz[["season", "posteam", "rz_td_rate"]],  on=["season", "posteam"], how="inner")
        .merge(drive[["season", "posteam", "scoring_rate", "avg_drive_epa"]],
               on=["season", "posteam"], how="inner")
    )
    merged = merged[merged["posteam"].notna() & (merged["posteam"] != "NA")]

    for col in ["epa_per_play", "success_rate", "total_wpa", "rz_td_rate",
                "scoring_rate", "avg_drive_epa"]:
        merged[f"{col}_rank"] = merged.groupby("season")[col].rank(
            ascending=False, method="min"
        ).astype(int)

    rank_cols = [c for c in merged.columns if c.endswith("_rank")]
    merged["composite_rank"] = merged[rank_cols].mean(axis=1).round(2)
    merged = merged.sort_values(["season", "composite_rank"])
    merged = merged.round(4)
    return _clean(merged)


def export_metrics_json() -> Path:
    WEB_DIR.mkdir(parents=True, exist_ok=True)

    epa   = _read_csv("epa_by_team.csv")
    sr    = _read_csv("success_rate_by_team.csv")
    wpa   = _read_csv("wpa_by_team.csv")
    rz    = _read_csv("redzone_efficiency.csv")
    drive = _read_csv("drive_efficiency.csv")

    for df in [wpa, drive]:
        df.drop(df[df["posteam"] == "NA"].index, inplace=True)

    composite = build_composite_rankings(epa, sr, wpa, rz, drive)

    epa_report    = _load_report("epa_model")
    wp_report     = _load_report("wp_model")
    success_report = _load_report("success_model")
    rz_report     = _load_report("rz_model")
    drive_report  = _load_report("drive_model")

    payload = {
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "seasons": [2021, 2022, 2023],
        "metrics": {
            "epa":              _clean(epa.round(4)),
            "success_rate":     _clean(sr.round(4)),
            "wpa":              _clean(wpa.round(4)),
            "redzone":          _clean(rz.round(4)),
            "drive_efficiency": _clean(drive.round(4)),
        },
        "composite_rankings": composite,
        "model_reports": {
            "epa":     epa_report,
            "wp":      wp_report,
            "success": success_report,
            "rz":      rz_report,
            "drive":   drive_report,
        },
    }

    out = WEB_DIR / "metrics.json"
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"metrics.json written → {out}")
    return out


def export_prediction_grid(epa_model=None, success_model=None) -> Path:
    #exports prediction grid for static web page predictor
    #loads models from disk if not provided
    from python.models.epa_model import EPAModel
    from python.models.success_model import SuccessModel
    from python.features.engineering import add_features

    if epa_model is None:
        epa_model = EPAModel.load()
    if success_model is None:
        success_model = SuccessModel.load()

    downs    = [1, 2, 3, 4]
    ydstogos = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25]
    yardlines = [5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 99]
    score_diffs = [-14, -7, 0, 7, 14]

    rows = []
    for d in downs:
        for yt in ydstogos:
            if yt > (d == 1 and 10 or 99):  #skip impossible states
                continue
            for yl in yardlines:
                for sd in score_diffs:
                    rows.append({
                        "down": d, "ydstogo": yt, "yardline_100": yl,
                        "score_differential": sd,
                        "half_seconds_remaining": 900,
                        "game_seconds_remaining": 1800,
                        "posteam_timeouts_remaining": 2,
                        "defteam_timeouts_remaining": 2,
                        "is_two_minute": 0, "is_final_two": 0, "is_4th_quarter": 0,
                        "is_red_zone": int(yl <= 20),
                        "is_goal_to_go": int(yl <= yt),
                        "shotgun_flag": 0, "no_huddle_flag": 0,
                        "play_type": "pass",
                    })

    grid_df = pd.DataFrame(rows)
    grid_df = add_features(grid_df)

    feat_epa     = [c for c in epa_model.feature_cols if c in grid_df.columns]
    feat_success = [c for c in success_model.feature_cols if c in grid_df.columns]

    grid_df["pred_epa"]     = epa_model.model.predict(grid_df[feat_epa])
    grid_df["pred_success"] = success_model.model.predict_proba(grid_df[feat_success])[:, 1]

    grid_df = grid_df[
        ["down", "ydstogo", "yardline_100", "score_differential", "pred_epa", "pred_success"]
    ].round(4)

    WEB_DIR.mkdir(parents=True, exist_ok=True)
    out = WEB_DIR / "prediction_grid.json"
    with open(out, "w") as f:
        json.dump(grid_df.to_dict(orient="records"), f)
    print(f"prediction_grid.json written → {out}  ({len(grid_df):,} rows)")
    return out


if __name__ == "__main__":
    export_metrics_json()
    try:
        export_prediction_grid()
    except Exception as e:
        print(f"skipped prediction grid (models not yet trained): {e}")
