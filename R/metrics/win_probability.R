#win_probability.r
#aggregates win probability added (wpa) from nflfastr's pre-computed wpa column

#param pbp: play-by-play tibble from nflfastr
#returns tibble with total_wpa and avg_wpa grouped by season and posteam
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
