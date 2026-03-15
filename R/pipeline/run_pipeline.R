# run_pipeline.R
# Orchestrates the full analytics pipeline: ingest -> compute -> save.

source("R/ingestion/load_pbp.R")
source("R/metrics/epa.R")
source("R/metrics/success_rate.R")
source("R/metrics/win_probability.R")
source("R/metrics/redzone.R")
source("R/metrics/drive_efficiency.R")
source("R/utils/helpers.R")

# --- Config ---
SEASONS <- 2021:2023

# --- Ingest ---
pbp_raw <- load_pbp(SEASONS)
pbp     <- filter_regular_season(pbp_raw)

# --- Compute metrics ---
epa_df    <- compute_epa(pbp)
sr_df     <- compute_success_rate(pbp)
wpa_df    <- compute_wpa(pbp)
rz_df     <- compute_redzone_efficiency(pbp)
drive_df  <- compute_drive_efficiency(pbp)

# --- Save outputs ---
save_output(epa_df,   "epa_by_team.csv")
save_output(sr_df,    "success_rate_by_team.csv")
save_output(wpa_df,   "wpa_by_team.csv")
save_output(rz_df,    "redzone_efficiency.csv")
save_output(drive_df, "drive_efficiency.csv")

message("Pipeline complete.")
