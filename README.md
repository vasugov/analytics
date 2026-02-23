# A live NFL analytics framework

## Features
- **Real-time metric computation**:
  - Expected Points Added (EPA)
  - Success Rate
  - Red Zone Efficiency
  - Drive-Level Efficiency
  - Dynamic Win Probability (WP)
- **Event-driven architecture** with in-memory state management
- **WebSocket API** for live frontend updates
- **Persistent logging** for replayability and historical analysis
- **Multi-game concurrency support**

## Architecture
1. **Data Ingestion Layer**: Collects and buffers live NFL play-by-play events (Kafka).  
2. **Event-Driven Engine**: Consumes events, updates game state, triggers metric computations (Python/Node.js, Redis).  
3. **Metrics Computation Layer**: Computes advanced analytics using vectorized operations (NumPy, pandas, Numba).  
4. **WebSocket / Frontend Layer**: Pushes live metrics to dashboards (React.js, D3.js, FastAPI/WebSockets).  
5. **Persistence Layer**: Logs events and stores metrics for replay and analysis (PostgreSQL, MongoDB, S3).
