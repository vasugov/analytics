#success_rate.r
#binary success metric: a play is counted successful when epa > 0

#param pbp: play-by-play tibble from nflfastr
#returns tibble with plays and success_rate grouped by season and posteam
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
