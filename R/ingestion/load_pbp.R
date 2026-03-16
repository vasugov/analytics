#load_pbp.r
#wraps nflfastr::load_pbp to pull play-by-play data for one or more seasons

library(nflfastR)
library(dplyr)

#load play-by-play data for a vector of seasons
#param seasons: integer vector e.g. 2020:2023
#returns tibble of raw play-by-play rows from nflfastr
load_pbp <- function(seasons) {
  message("Loading play-by-play data for seasons: ", paste(seasons, collapse = ", "))
  pbp <- nflfastR::load_pbp(seasons)
  return(pbp)
}

#serialize raw pbp tibble to rds for caching between runs
#param pbp: play-by-play tibble
#param path: destination file path (.rds)
save_pbp <- function(pbp, path = "data/raw/pbp.rds") {
  saveRDS(pbp, file = path)
  message("Saved play-by-play data to: ", path)
}
