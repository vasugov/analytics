"""
loader.py
Utilities for loading processed metric outputs (CSVs) produced by the R pipeline
into Python for downstream modeling and API use.
"""

import pandas as pd
from pathlib import Path

OUTPUTS_DIR = Path(__file__).resolve().parents[2] / "data" / "outputs"


def load_metric(filename: str) -> pd.DataFrame:
    """Load a metric CSV from the outputs directory."""
    path = OUTPUTS_DIR / filename
    if not path.exists():
        raise FileNotFoundError(f"Metric file not found: {path}")
    return pd.read_csv(path)


def load_all_metrics() -> dict[str, pd.DataFrame]:
    """Load all available metric outputs into a dict keyed by metric name."""
    files = {
        "epa":             "epa_by_team.csv",
        "success_rate":    "success_rate_by_team.csv",
        "wpa":             "wpa_by_team.csv",
        "redzone":         "redzone_efficiency.csv",
        "drive_efficiency":"drive_efficiency.csv",
    }
    return {name: load_metric(fname) for name, fname in files.items()}
