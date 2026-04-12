#trainer.py
#orchestrates training of all five nfl models
#usage: python -m python.training.trainer [--model epa|wp|success|rz|drive|all]

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd

from python.features.engineering import add_features, get_feature_cols, time_split
from python.features.selection import top_features
from python.models.epa_model import EPAModel
from python.models.wp_model import WPModel, WP_FEATURES
from python.models.success_model import SuccessModel
from python.models.rz_model import RZModel, RZ_FEATURES
from python.models.drive_model import DriveModel, DRIVE_FEATURES, DRIVE_CLASSES
from python.pipeline.loader import load_metric

OUTPUTS_DIR = Path(__file__).resolve().parents[2] / "data" / "outputs"
MODELS_DIR  = Path(__file__).resolve().parents[2] / "models" / "saved"
REPORTS_DIR = Path(__file__).resolve().parents[2] / "models" / "reports"


def load_play_features() -> pd.DataFrame:
    path = OUTPUTS_DIR / "play_features.csv"
    if not path.exists():
        raise FileNotFoundError(
            f"play_features.csv not found at {path}. "
            "Run the R pipeline first: Rscript R/pipeline/run_pipeline.R"
        )
    df = pd.read_csv(path)
    print(f"loaded {len(df):,} plays")
    return df


def _save_report(name: str, metrics: dict) -> None:
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    path = REPORTS_DIR / f"{name}.json"
    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)
    print(f"  report saved → {path}")


#individual trainers

def train_epa(df: pd.DataFrame) -> EPAModel:
    print("\n[epa model]")
    df_f = add_features(df)
    feat  = get_feature_cols()
    feat  = [c for c in feat if c in df_f.columns]
    train, val = time_split(df_f)
    X_tr = train[feat].astype(float)
    X_v  = val[feat].astype(float)
    y_tr = train["epa"]
    y_v  = val["epa"]

    model = EPAModel()
    t0 = time.time()
    model.fit_with_eval(X_tr, y_tr, X_v, y_v)
    elapsed = time.time() - t0

    tr_metrics = model.evaluate(X_tr, y_tr)
    v_metrics  = model.evaluate(X_v,  y_v)
    print(f"  train {tr_metrics}  val {v_metrics}  ({elapsed:.0f}s)")

    fi = top_features(model.model, feat, n=20).to_dict(orient="records")
    _save_report("epa_model", {
        "train": tr_metrics, "val": v_metrics,
        "elapsed_s": round(elapsed, 1),
        "feature_importance": fi,
    })
    model.save()
    return model


def train_wp(df: pd.DataFrame) -> WPModel:
    print("\n[wp model]")
    #need win outcome — join game results
    #posteam_won: 1 if posteam's final score > defteam's final score
    df_f = add_features(df).copy()
    if "posteam_score_post" not in df_f.columns or "defteam_score_post" not in df_f.columns:
        print("  warning: win label columns not found — skipping wp model")
        return None

    df_f["posteam_won"] = (
        df_f["posteam_score_post"] > df_f["defteam_score_post"]
    ).astype(int)

    feat  = [c for c in WP_FEATURES if c in df_f.columns]
    train, val = time_split(df_f)
    X_tr, y_tr = train[feat], train["posteam_won"]
    X_v,  y_v  = val[feat],   val["posteam_won"]

    model = WPModel()
    t0 = time.time()
    model.feature_cols = feat
    model.fit_with_eval(X_tr, y_tr, X_v, y_v)
    elapsed = time.time() - t0

    tr_metrics = model.evaluate(X_tr, y_tr)
    v_metrics  = model.evaluate(X_v,  y_v)
    print(f"  train {tr_metrics}  val {v_metrics}  ({elapsed:.0f}s)")

    fi = top_features(model.model, feat, n=15).to_dict(orient="records")
    _save_report("wp_model", {
        "train": tr_metrics, "val": v_metrics,
        "elapsed_s": round(elapsed, 1),
        "feature_importance": fi,
    })
    model.save()
    return model


def train_success(df: pd.DataFrame) -> SuccessModel:
    print("\n[success model]")
    df_f = add_features(df)
    feat  = get_feature_cols()
    feat  = [c for c in feat if c in df_f.columns]
    train, val = time_split(df_f)
    X_tr = train[feat].astype(float)
    X_v  = val[feat].astype(float)
    y_tr = train["success"]
    y_v  = val["success"]

    model = SuccessModel()
    t0 = time.time()
    model.fit_with_eval(X_tr, y_tr, X_v, y_v)
    elapsed = time.time() - t0

    tr_metrics = model.evaluate(X_tr, y_tr)
    v_metrics  = model.evaluate(X_v,  y_v)
    print(f"  train {tr_metrics}  val {v_metrics}  ({elapsed:.0f}s)")

    fi = top_features(model.model, feat, n=15).to_dict(orient="records")
    _save_report("success_model", {
        "train": tr_metrics, "val": v_metrics,
        "elapsed_s": round(elapsed, 1),
        "feature_importance": fi,
    })
    model.save()
    return model


def train_rz(df: pd.DataFrame) -> RZModel:
    print("\n[red zone model]")
    df_f = add_features(df)
    rz   = df_f[df_f["yardline_100"] <= 20].copy()
    print(f"  {len(rz):,} red zone plays")
    feat  = [c for c in RZ_FEATURES if c in rz.columns]
    train, val = time_split(rz)
    X_tr = train[feat].astype(float)
    X_v  = val[feat].astype(float)
    y_tr = train["is_td_play"]
    y_v  = val["is_td_play"]

    model = RZModel()
    t0 = time.time()
    model.feature_cols = feat
    model.fit_with_eval(X_tr, y_tr, X_v, y_v)
    elapsed = time.time() - t0

    tr_metrics = model.evaluate(X_tr, y_tr)
    v_metrics  = model.evaluate(X_v,  y_v)
    print(f"  train {tr_metrics}  val {v_metrics}  ({elapsed:.0f}s)")

    fi = top_features(model.model, feat, n=12).to_dict(orient="records")
    _save_report("rz_model", {
        "train": tr_metrics, "val": v_metrics,
        "elapsed_s": round(elapsed, 1),
        "feature_importance": fi,
    })
    model.save()
    return model


def train_drive(df: pd.DataFrame) -> DriveModel:
    print("\n[drive outcome model]")
    df_f = add_features(df)

    if "drive" not in df_f.columns or "fixed_drive_result" not in df_f.columns:
        print("  warning: drive/fixed_drive_result columns not in play_features — "
              "re-run Rscript R/pipeline/run_pipeline.R to include them, then retrain")
        return None

    #use first play of each drive as the predictor state
    drive_starts = (
        df_f.sort_values(["game_id", "play_id"])
            .groupby(["game_id", "season", "drive"], as_index=False)
            .first()
    )

    label_map = {
        "Touchdown": 0, "Field goal": 1, "Punt": 2,
        "Interception": 3, "Fumble": 3,
        "Missed field goal": 4, "End of half": 4, "Turnover on downs": 4,
    }

    if "fixed_drive_result" not in drive_starts.columns:
        print("  warning: fixed_drive_result not in play_features — skipping drive model")
        return None

    drive_starts["drive_label"] = drive_starts["fixed_drive_result"].map(label_map).fillna(4).astype(int)
    feat  = [c for c in DRIVE_FEATURES if c in drive_starts.columns]
    train, val = time_split(drive_starts)
    X_tr = train[feat].astype(float)
    X_v  = val[feat].astype(float)
    y_tr = train["drive_label"]
    y_v  = val["drive_label"]

    model = DriveModel()
    t0 = time.time()
    model.feature_cols = feat
    model.fit_with_eval(X_tr, y_tr, X_v, y_v)
    elapsed = time.time() - t0

    tr_metrics = model.evaluate(X_tr, y_tr)
    v_metrics  = model.evaluate(X_v,  y_v)
    print(f"  train {tr_metrics}  val {v_metrics}  ({elapsed:.0f}s)")

    fi = top_features(model.model, feat, n=12).to_dict(orient="records")
    _save_report("drive_model", {
        "train": tr_metrics, "val": v_metrics,
        "elapsed_s": round(elapsed, 1),
        "feature_importance": fi,
    })
    model.save()
    return model


#prediction grid export

def export_prediction_grid(epa_model: EPAModel, success_model: SuccessModel) -> None:
    #exports (down x ydstogo x yardline x score_diff) prediction grid as json for web page
    from python.export.json_exporter import export_prediction_grid as _export
    _export(epa_model, success_model)


#main

def train_all() -> None:
    df = load_play_features()
    epa     = train_epa(df)
    success = train_success(df)
    train_rz(df)
    train_drive(df)
    train_wp(df)
    export_prediction_grid(epa, success)
    print("\nall models trained and saved to models/saved/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", default="all",
                        choices=["all", "epa", "wp", "success", "rz", "drive"])
    args = parser.parse_args()

    df = load_play_features()
    dispatch = {
        "epa":     lambda: train_epa(df),
        "wp":      lambda: train_wp(df),
        "success": lambda: train_success(df),
        "rz":      lambda: train_rz(df),
        "drive":   lambda: train_drive(df),
        "all":     train_all,
    }
    dispatch[args.model]()
