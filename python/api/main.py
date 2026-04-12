#main.py
#nfl analytics fastapi — serves aggregate metrics, model predictions, and team profiles
#run: uvicorn python.api.main:app --reload

from __future__ import annotations

from pathlib import Path
from typing import Optional
import json

import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from python.pipeline.loader import load_all_metrics

MODELS_DIR  = Path(__file__).resolve().parents[2] / "models" / "saved"
REPORTS_DIR = Path(__file__).resolve().parents[2] / "models" / "reports"


app = FastAPI(title="NFL Analytics API", version="1.0.0")

#allow github pages frontend to call this api
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


#lazy-loaded model cache

_models: dict = {}

def _get_model(name: str):
    if name not in _models:
        import joblib
        path = MODELS_DIR / f"{name}.pkl"
        if not path.exists():
            return None
        _models[name] = joblib.load(path)
    return _models[name]


#request/response schemas

class PlayState(BaseModel):
    down: int               = Field(..., ge=1, le=4)
    ydstogo: int            = Field(..., ge=1, le=99)
    yardline_100: int       = Field(..., ge=1, le=99)
    score_differential: int = Field(default=0)
    half_seconds_remaining: int = Field(default=900, ge=0, le=1800)
    game_seconds_remaining: int = Field(default=1800, ge=0, le=3600)
    posteam_timeouts_remaining: int = Field(default=2, ge=0, le=3)
    defteam_timeouts_remaining: int = Field(default=2, ge=0, le=3)
    play_type: str          = Field(default="pass")


class PlayPrediction(BaseModel):
    pred_epa: Optional[float]
    pred_success_prob: Optional[float]
    pred_rz_td_prob: Optional[float]
    model_available: bool


#health

@app.get("/health")
def health():
    return {"status": "ok", "models_dir": str(MODELS_DIR)}


#metrics endpoints

@app.get("/metrics/{metric}")
def get_metric(metric: str, season: Optional[int] = None, team: Optional[str] = None):
    valid = {"epa", "success_rate", "wpa", "redzone", "drive_efficiency"}
    if metric not in valid:
        raise HTTPException(status_code=404, detail=f"metric '{metric}' not found. valid: {valid}")
    all_metrics = load_all_metrics()
    df = all_metrics[metric]
    if season:
        df = df[df["season"] == season]
    if team:
        col = "posteam" if "posteam" in df.columns else df.columns[1]
        df = df[df[col].str.upper() == team.upper()]
    return df.to_dict(orient="records")


@app.get("/teams/{team}/profile")
def team_profile(team: str, season: Optional[int] = None):
    all_metrics = load_all_metrics()
    result = {}
    for name, df in all_metrics.items():
        if "posteam" not in df.columns:
            continue
        sub = df[df["posteam"].str.upper() == team.upper()]
        if season:
            sub = sub[sub["season"] == season]
        result[name] = sub.to_dict(orient="records")
    if not any(result.values()):
        raise HTTPException(status_code=404, detail=f"team '{team}' not found")
    return result


#model prediction endpoints

@app.post("/predict/play", response_model=PlayPrediction)
def predict_play(state: PlayState):
    from python.features.engineering import add_features

    row = pd.DataFrame([state.dict()])
    row = add_features(row)

    epa_model     = _get_model("epa_model")
    success_model = _get_model("success_model")
    rz_model      = _get_model("rz_model")

    if epa_model is None:
        return PlayPrediction(
            pred_epa=None, pred_success_prob=None, pred_rz_td_prob=None,
            model_available=False
        )

    def safe_predict(model, row, proba=False):
        try:
            feat = [c for c in model.feature_cols if c in row.columns]
            if proba:
                return float(model.model.predict_proba(row[feat])[:, 1][0])
            return float(model.model.predict(row[feat])[0])
        except Exception:
            return None

    pred_epa     = safe_predict(epa_model, row, proba=False)
    pred_success = safe_predict(success_model, row, proba=True) if success_model else None
    pred_rz      = None
    if rz_model and state.yardline_100 <= 20:
        pred_rz = safe_predict(rz_model, row, proba=True)

    return PlayPrediction(
        pred_epa=round(pred_epa, 4) if pred_epa is not None else None,
        pred_success_prob=round(pred_success, 4) if pred_success is not None else None,
        pred_rz_td_prob=round(pred_rz, 4) if pred_rz is not None else None,
        model_available=True,
    )


@app.get("/models/feature-importance/{model_name}")
def feature_importance(model_name: str):
    path = REPORTS_DIR / f"{model_name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"no report for '{model_name}'")
    with open(path) as f:
        report = json.load(f)
    return report.get("feature_importance", [])


@app.get("/models/report/{model_name}")
def model_report(model_name: str):
    path = REPORTS_DIR / f"{model_name}.json"
    if not path.exists():
        raise HTTPException(status_code=404, detail=f"no report for '{model_name}'")
    with open(path) as f:
        return json.load(f)
