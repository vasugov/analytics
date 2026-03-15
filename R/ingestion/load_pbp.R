# load_pbp.R
# Loads play-by-play data using nflfastR for one or more seasons.

library(nflfastR)
library(dplyr)

#' Load play-by-play data for given seasons
#'
#' @param seasons Integer vector of seasons (e.g. 2020:2023)
#' @return A tibble of play-by-play data
load_pbp <- function(seasons) {
  message("Loading play-by-play data for seasons: ", paste(seasons, collapse = ", "))
  pbp <- nflfastR::load_pbp(seasons)
  return(pbp)
}

#' Save raw play-by-play data to disk
#'
#' @param pbp Play-by-play tibble
#' @param path Output file path (.rds)
save_pbp <- function(pbp, path = "data/raw/pbp.rds") {
  saveRDS(pbp, file = path)
  message("Saved play-by-play data to: ", path)
}
