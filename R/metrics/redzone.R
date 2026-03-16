#redzone.r
#computes red zone td rate using yardline_100 <= 20 as the entry threshold

#param pbp: play-by-play tibble from nflfastr
#returns tibble with rz_plays, rz_tds, and rz_td_rate grouped by season and posteam
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
