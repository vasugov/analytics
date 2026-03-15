# success_rate.R
# Success rate metric: a play is successful if EPA > 0.

#' Compute success rate by team and season
#'
#' @param pbp Play-by-play tibble from nflfastR
#' @return A tibble with success rate by posteam
compute_success_rate <- function(pbp) {
  pbp |>
    dplyr::filter(!is.na(epa), play_type %in% c("pass", "run")) |>
    dplyr::group_by(season, posteam) |>
    dplyr::summarise(
      plays        = dplyr::n(),
      success_rate = mean(epa > 0, na.rm = TRUE),
      .groups = "drop"
    ) |>
    dplyr::arrange(season, dplyr::desc(success_rate))
}
