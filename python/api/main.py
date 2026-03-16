#fastapi app entry point for the nfl analytics api
#routes are stubs pending real-time data integration

from fastapi import FastAPI

app = FastAPI(title="NFL Analytics API", version="0.1.0")


@app.get("/health")
def health():
    return {"status": "ok"}


#planned endpoints once streaming layer is wired up
#@app.get("/metrics/epa") -> serve aggregated epa by team and season
#@app.get("/metrics/wp") -> serve win probability indexed by game state
#@app.websocket("/ws/live") -> push play-by-play events to clients in real time
