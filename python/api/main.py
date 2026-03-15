"""
main.py
FastAPI application entry point (placeholder for future real-time API).
"""

from fastapi import FastAPI

app = FastAPI(title="NFL Analytics API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


# Future routes:
# @app.get("/metrics/epa")       -> serve EPA data
# @app.get("/metrics/wp")        -> serve win probability
# @app.websocket("/ws/live")     -> real-time play-by-play stream
