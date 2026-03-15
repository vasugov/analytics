# drive_efficiency.R
# Drive-level efficiency metrics.

#' Compute drive-level efficiency by team and season
#'
#' @param pbp Play-by-play tibble from nflfastR
#' @return A tibble summarising drive outcomes by posteam
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
