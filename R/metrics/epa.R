# epa.R
# Expected Points Added (EPA) metric computation.

#' Compute per-play EPA summary by team and season
#'
#' @param pbp Play-by-play tibble from nflfastR
#' @return A tibble with EPA per play by posteam
compute_epa <- function(pbp) {
  pbp |>
    dplyr::filter(!is.na(epa), play_type %in% c("pass", "run")) |>
    dplyr::group_by(season, posteam) |>
    dplyr::summarise(
      plays       = dplyr::n(),
      total_epa   = sum(epa, na.rm = TRUE),
      epa_per_play = mean(epa, na.rm = TRUE),
      .groups = "drop"
    ) |>
    dplyr::arrange(season, dplyr::desc(epa_per_play))
}
