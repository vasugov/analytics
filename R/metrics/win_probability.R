# win_probability.R
# Win probability (WP) metric computation.

#' Compute average win probability added (WPA) by team and season
#'
#' @param pbp Play-by-play tibble from nflfastR
#' @return A tibble with total WPA by posteam
compute_wpa <- function(pbp) {
  pbp |>
    dplyr::filter(!is.na(wpa)) |>
    dplyr::group_by(season, posteam) |>
    dplyr::summarise(
      total_wpa = sum(wpa, na.rm = TRUE),
      avg_wpa   = mean(wpa, na.rm = TRUE),
      .groups = "drop"
    ) |>
    dplyr::arrange(season, dplyr::desc(total_wpa))
}
