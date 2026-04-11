#features.r
#exports a flat, play-level feature dataset for ml training
#each row = one pass or run play with game-state context and outcome labels

library(dplyr)

compute_features <- function(pbp) {
  pbp |>
    dplyr::filter(
      play_type %in% c("pass", "run"),
      !is.na(down),
      !is.na(ydstogo),
      !is.na(yardline_100),
      !is.na(epa),
      !is.na(half_seconds_remaining),
      !is.na(game_seconds_remaining),
      !is.na(score_differential)
    ) |>
    dplyr::mutate(
      #binary outcome labels
      success       = as.integer(epa > 0),
      is_td_play    = as.integer(!is.na(touchdown) & touchdown == 1),
      is_turnover   = as.integer(
        (!is.na(interception) & interception == 1) |
        (!is.na(fumble_lost)  & fumble_lost  == 1)
      ),
      first_down_converted = as.integer(!is.na(first_down_rush) | !is.na(first_down_pass)),
      #situational flags
      is_two_minute  = as.integer(half_seconds_remaining <= 120),
      is_final_two   = as.integer(game_seconds_remaining <= 120),
      is_4th_quarter = as.integer(game_seconds_remaining <= 900),
      is_red_zone    = as.integer(yardline_100 <= 20),
      is_goal_to_go  = as.integer(!is.na(goal_to_go) & goal_to_go == 1),
      #shotgun and no-huddle as integers
      shotgun_flag   = as.integer(!is.na(shotgun) & shotgun == 1),
      no_huddle_flag = as.integer(!is.na(no_huddle) & no_huddle == 1)
    ) |>
    dplyr::select(
      #identifiers
      game_id, play_id, season, week, posteam, defteam,
      #drive identifiers (needed for drive outcome model)
      drive,
      dplyr::any_of("fixed_drive_result"),
      #win outcome (needed for win probability model)
      dplyr::any_of(c("result", "posteam_score_post", "defteam_score_post")),
      #core game-state features (model inputs)
      down, ydstogo, yardline_100,
      score_differential,
      half_seconds_remaining,
      game_seconds_remaining,
      posteam_timeouts_remaining,
      defteam_timeouts_remaining,
      is_two_minute, is_final_two, is_4th_quarter,
      is_red_zone, is_goal_to_go,
      shotgun_flag, no_huddle_flag,
      play_type,
      #outcomes (targets)
      yards_gained,
      epa, wpa,
      success,
      is_td_play,
      is_turnover,
      first_down_converted,
      touchdown,
      interception,
      fumble_lost
    )
}
