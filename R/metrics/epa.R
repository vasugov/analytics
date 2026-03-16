#epa.r
#computes expected points added (epa) per play aggregated by team and season

#param pbp: play-by-play tibble from nflfastr
#returns tibble with plays, total_epa, and epa_per_play grouped by season and posteam
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
