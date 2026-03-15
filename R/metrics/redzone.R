# redzone.R
# Red zone efficiency metric.

#' Compute red zone efficiency (TD rate) by team and season
#'
#' @param pbp Play-by-play tibble from nflfastR
#' @return A tibble with red zone TD rate by posteam
compute_redzone_efficiency <- function(pbp) {
  pbp |>
    dplyr::filter(yardline_100 <= 20, play_type %in% c("pass", "run")) |>
    dplyr::group_by(season, posteam) |>
    dplyr::summarise(
      rz_plays = dplyr::n(),
      rz_tds   = sum(touchdown == 1, na.rm = TRUE),
      rz_td_rate = rz_tds / rz_plays,
      .groups = "drop"
    ) |>
    dplyr::arrange(season, dplyr::desc(rz_td_rate))
}
