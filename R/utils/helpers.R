#helpers.r
#shared utility functions used across the pipeline

library(dplyr)

#drops postseason rows so metrics only reflect regular season sample
filter_regular_season <- function(pbp) {
  pbp |> dplyr::filter(season_type == "REG")
}

#writes a tibble to csv under data/outputs using the given filename
save_output <- function(df, filename) {
  path <- file.path("data/outputs", filename)
  readr::write_csv(df, path)
  message("Saved: ", path)
}
