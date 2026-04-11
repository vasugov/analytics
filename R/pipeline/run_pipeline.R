#run_pipeline.r
#orchestrates the full analytics pipeline: ingest -> compute -> save

source("R/ingestion/load_pbp.R")
source("R/metrics/epa.R")
source("R/metrics/success_rate.R")
source("R/metrics/win_probability.R")
source("R/metrics/redzone.R")
source("R/metrics/drive_efficiency.R")
source("R/metrics/features.R")
source("R/utils/helpers.R")

#config
SEASONS <- 2021:2023

#ingest
pbp_raw <- load_pbp(SEASONS)
pbp     <- filter_regular_season(pbp_raw)

#compute aggregate metrics
epa_df    <- compute_epa(pbp)
sr_df     <- compute_success_rate(pbp)
wpa_df    <- compute_wpa(pbp)
rz_df     <- compute_redzone_efficiency(pbp)
drive_df  <- compute_drive_efficiency(pbp)

#compute play-level feature dataset for ml training
features_df <- compute_features(pbp)

#save aggregate outputs
save_output(epa_df,      "epa_by_team.csv")
save_output(sr_df,       "success_rate_by_team.csv")
save_output(wpa_df,      "wpa_by_team.csv")
save_output(rz_df,       "redzone_efficiency.csv")
save_output(drive_df,    "drive_efficiency.csv")

#save play-level ml dataset
save_output(features_df, "play_features.csv")

message("Pipeline complete — ", nrow(features_df), " plays exported for ml")
