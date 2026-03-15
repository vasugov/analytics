# helpers.R
# Shared utility functions used across the pipeline.

library(dplyr)

#' Filter play-by-play to regular season only
filter_regular_season <- function(pbp) {
  pbp |> dplyr::filter(season_type == "REG")
}

#' Save a tibble as a CSV to the outputs folder
save_output <- function(df, filename) {
  path <- file.path("data/outputs", filename)
  readr::write_csv(df, path)
  message("Saved: ", path)
}
