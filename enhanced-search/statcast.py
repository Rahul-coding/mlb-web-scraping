import pandas as pd
import statsapi
from pybaseball import (
    playerid_lookup,
    statcast_batter_expected_stats,
    statcast_batter_exitvelo_barrels,
    statcast_pitcher_expected_stats,
    statcast_pitcher_exitvelo_barrels,
)

def get_stats(players, comparison_mode="Batters", year=2026): 
    is_pitching = comparison_mode == "Pitchers"
    expected_stats_leaderboard = (
        statcast_pitcher_expected_stats(year)
        if is_pitching
        else statcast_batter_expected_stats(year)
    )
    barrel_leaderboard = (
        statcast_pitcher_exitvelo_barrels(year)
        if is_pitching
        else statcast_batter_exitvelo_barrels(year)
    )

    dfs = []
    for player in players:
        player_parts = player.strip().split(" ")
        first_name = player_parts[0]
        last_name = player_parts[1] 

        player_info = playerid_lookup(last_name, first_name)

        if player_info.empty:
            print(f"Could not find {first_name} {last_name}")
            continue
        
        #get the player
        mlbam_id = player_info.iloc[0]["key_mlbam"]
        
        #pull stats
        player_stats = expected_stats_leaderboard[expected_stats_leaderboard["player_id"] == mlbam_id].copy()

        player_barrels = barrel_leaderboard [barrel_leaderboard ["player_id"] == mlbam_id]["brl_percent"].copy()

        if player_stats.empty:
            statcast_label = "pitcher" if is_pitching else "batter"
            print(f"No Statcast data found for {first_name} {last_name} ({statcast_label}) in {year}")
            continue

        player_stats["player"] = f"{first_name} {last_name}"
        player_stats["brl_percent"] = player_barrels.values[0] if not player_barrels.empty else 0

        # If pitching, try to augment with season strikeouts/walks to compute K% and BB%
        if is_pitching:
            try:
                season_stats = statsapi.player_stat_data(int(mlbam_id), "pitching", season=year)
                stats_entries = season_stats.get("stats", [])
                if stats_entries and stats_entries[0].get("stats"):
                    s = stats_entries[0]["stats"]
                    so = s.get("strikeOuts") or s.get("strikeouts") or 0
                    bb = s.get("baseOnBalls") or s.get("walks") or 0
                    # Use 'pa' from player_stats if present (plate appearances against)
                    pa = player_stats.iloc[0].get("pa", None)
                    if pa and pa > 0:
                        k_pct_series = pd.Series([ (so / pa) * 100 ])
                        bb_pct_series = pd.Series([ (bb / pa) * 100 ])
                    else:
                        k_pct_series = pd.Series([ None ])
                        bb_pct_series = pd.Series([ None ])
                else:
                    k_pct_series = pd.Series([ None ])
                    bb_pct_series = pd.Series([ None ])
            except Exception:
                k_pct_series = pd.Series([ None ])
                bb_pct_series = pd.Series([ None ])

            # Attach computed rates (align length if needed)
            player_stats = player_stats.reset_index(drop=True)
            player_stats["k_pct"] = k_pct_series.values[0]
            player_stats["bb_pct"] = bb_pct_series.values[0]

        dfs.append(player_stats)

    if not dfs:
        print("No player data was collected.")
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    if not df.empty:
        if is_pitching:
            # Attempt to expose pitcher-specific metrics when present in the pybaseball output.
            # Look for common column variants and map them into a consistent output.
            cols = df.columns
            def pick(col_options, default=None):
                for c in col_options:
                    if c in cols:
                        return df[c]
                return pd.Series([default] * len(df))

            xera = pick(["xera", "est_era", "x_era", "xERA"], default=None)
            xba = pick(["xba", "est_ba", "est_xba", "xBA", "est_ba"], default=None)
            k_pct = pick(["k_pct", "k%", "k_rate", "k_rate_pct", "k_pct_pitch"], default=None)
            bb_pct = pick(["bb_pct", "bb%", "bb_rate", "bb_rate_pct", "bb_pct_pitch"], default=None)

            comparison = pd.DataFrame({
                "player": df["player"],
                "xera": xera,
                "xba": xba,
                "k_pct": k_pct,
                "bb_pct": bb_pct,
                "brl_percent": df.get("brl_percent", pd.Series([0] * len(df))),
            })
            return comparison
        else:
            comparison = df[["player", "est_ba", "est_slg", "est_woba", "brl_percent"]]
            return comparison