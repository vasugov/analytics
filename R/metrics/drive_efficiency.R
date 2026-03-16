#drive_efficiency.r
#two-pass aggregation: first collapses to drive level, then rolls up to team/season

#param pbp: play-by-play tibble from nflfastr
#returns tibble with drives, td_drives, scoring_rate, and avg_drive_epa by season and posteam
compute_drive_efficiency <- function(pbp) {
  pbp |>
    dplyr::filter(!is.na(drive), !is.na(fixed_drive_result)) |>
    dplyr::group_by(season, posteam, game_id, drive) |>
    dplyr::summarise(
      drive_result = dplyr::last(fixed_drive_result),
      drive_plays  = dplyr::n(),
      drive_epa    = sum(epa, na.rm = TRUE),
      .groups = "drop"
    ) |>
    dplyr::group_by(season, posteam) |>
    dplyr::summarise(
      drives         = dplyr::n(),
      td_drives      = sum(drive_result == "Touchdown", na.rm = TRUE),
      scoring_rate   = td_drives / drives,
      avg_drive_epa  = mean(drive_epa, na.rm = TRUE),
      .groups = "drop"
    ) |>
    dplyr::arrange(season, dplyr::desc(scoring_rate))
}
