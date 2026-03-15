# NFL Analytics Framework (Research Prototype)

[![Launch in Binder](https://mybinder.org/badge_logo.svg)](https://mybinder.org/v2/gh/vasugov/analytics/main?labpath=notebooks%2Flooks%2Fmetrics1.ipynb)

A research-oriented analytics framework for computing advanced football
metrics from play-by-play data. The system processes historical game
events and computes metrics such as Expected Points Added (EPA) and Win
Probability (WP).

The current version operates on historical datasets using **nflfastR**,
serving as a prototype for a future real-time analytics pipeline.

------------------------------------------------------------------------

# Project Goal

This project explores how modern analytics infrastructure could be built
for live football analysis.

The current implementation focuses on:

-   building metric computation pipelines
-   validating statistical models
-   designing scalable system architecture

Future versions aim to support **real-time ingestion and streaming
analytics during live games**.

------------------------------------------------------------------------

# Current Features

## Advanced Metric Computation

Using historical play-by-play data, the framework computes:

-   **Expected Points Added (EPA)**
-   **Success Rate**
-   **Red Zone Efficiency**
-   **Drive-Level Efficiency**
-   **Win Probability (WP)**

These metrics are computed across full games or seasons to analyze team
performance and strategy.

------------------------------------------------------------------------

## Historical Data Pipeline

Game data is sourced from:

-   **nflfastR play-by-play datasets**

The pipeline processes play events sequentially to simulate how a live
analytics engine would update game state.

------------------------------------------------------------------------

## Prototype Analytics Engine

The current engine:

-   processes play-by-play events sequentially
-   maintains game state in memory
-   updates metrics after each play

Although the data is historical, the structure mimics a **real-time
event-driven system**.

------------------------------------------------------------------------

# Planned Features

Future versions of the framework will include:

## Real-Time Data Ingestion

-   live play-by-play streams
-   event queue architecture
-   real-time metric updates

Potential technologies:

-   **Apache Kafka**
-   **Redis Streams**

------------------------------------------------------------------------

## Live Analytics Streaming

Metrics will be pushed to dashboards via:

-   WebSocket APIs
-   real-time visualization tools

Potential stack:

-   **FastAPI**
-   **React**
-   **D3.js**

------------------------------------------------------------------------

## Persistent Storage

For replay and historical analysis:

-   **PostgreSQL**
-   **MongoDB**
-   **Cloud Object Storage (S3)**

------------------------------------------------------------------------

# Example Use Cases

-   evaluating coaching decisions
-   analyzing personnel packages
-   game strategy optimization
-   research into probabilistic football models

------------------------------------------------------------------------

# Research Focus

This project sits at the intersection of:

-   sports analytics
-   distributed systems
-   statistical modeling
-   real-time data processing

------------------------------------------------------------------------

# Usage

## Run in the browser (no setup required)

Click the **Launch in Binder** badge above. Binder will build the environment
and open the metrics notebook directly in your browser. No installs needed.

Once open, click **Run All** (or Shift+Enter through each cell) to generate
all charts.

## Run locally

**Requirements:** R, Python 3.x

1. Clone the repo

        git clone https://github.com/vasugov/analytics.git
        cd analytics

2. Install R packages (one-time)

        Rscript -e "install.packages(c('nflfastR', 'dplyr', 'readr'), repos='https://cloud.r-project.org')"

3. Run the R pipeline to generate metric CSVs

        Rscript R/pipeline/run_pipeline.R

4. Install Python dependencies

        pip install -r requirements.txt

5. Open the notebook

        python -m jupyter notebook notebooks/looks/metrics1.ipynb

