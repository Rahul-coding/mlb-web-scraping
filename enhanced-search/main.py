import streamlit as st
import statsapi
import pandas as pd
import numpy as np
import json
import statcast

# --- Keep all your existing setup, layout, and loops exactly the same ---
playerId = 0
hittingStats = ["gamesPlayed", "runs", "doubles", "triples", "homeRuns", "strikeOuts", "baseOnBalls", "avg", "ops", "stolenBases"]
pitchingStats = ["gamesPlayed", "inningsPitched", "wins", "losses", "baseOnBalls", "strikeOuts", "avg", "era", "whip", "runs", "svhd", "blownSaves"]
lowerBetter = ["era", "whip", "avg"]

hittersStats = []
pitchersStats = []

with st.container(horizontal_alignment="right"):
    col_title, col_info = st.columns([7, 1])
    with col_info:
        st.button("Info", icon=":material/help:", help="Enter names...")

player = st.text_input("Player Names", placeholder="Aaron Judge, Chase Burns")
comparison_mode = st.radio(
    "Compare",
    ["Batters", "Pitchers"],
    horizontal=True,
)

# We use session_state to save the expected stats dataframe across button presses
if "df_expected" not in st.session_state:
    st.session_state.df_expected = None
if "df_expected_mode" not in st.session_state:
    st.session_state.df_expected_mode = None

if st.session_state.df_expected_mode != comparison_mode:
    st.session_state.df_expected = None

if st.button("Lookup Player(s)"):
    players = [player_item.strip() for player_item in player.split(",") if player_item.strip()]
    
    for player_item in players:
        result = statsapi.lookup_player(player_item)
        if result:
            position = result[0]['primaryPosition']['code']
            playerId = result[0]['id']
            fullName = result[0]['fullName']
            teamName = (statsapi.lookup_team(result[0]['currentTeam']['id']))[0].get('name')

            if comparison_mode == "Pitchers":
                stats = statsapi.player_stat_data(playerId, "pitching", season="2026")
                stats_entries = stats.get('stats', [])
                if not stats_entries or not stats_entries[0].get('stats'):
                    st.write(f"No pitching stats found for '{fullName}' in 2026.")
                    continue

                unfilteredStats = stats_entries[0]['stats']
                filteredStats = {"Name": fullName, "Team": teamName}
                for stat in pitchingStats:
                    if stat == "svhd":
                        filteredStats[stat] = unfilteredStats.get('saves', 0) + unfilteredStats.get('holds', 0)
                    elif stat in unfilteredStats:
                        filteredStats[stat] = unfilteredStats[stat]
                    else:
                        filteredStats[stat] = 0
                pitchersStats.append(filteredStats)
            else: 
                stats = statsapi.player_stat_data(playerId, "hitting", season="2026")
                stats_entries = stats.get('stats', [])
                if not stats_entries or not stats_entries[0].get('stats'):
                    st.write(f"No hitting stats found for '{fullName}' in 2026.")
                    continue

                unfilteredStats = stats_entries[0]['stats']
                filteredStats = {"Name": fullName, "Team": teamName}
                for stat in hittingStats:
                    if stat in unfilteredStats:
                        filteredStats[stat] = unfilteredStats[stat]
                    else:
                        filteredStats[stat] = "N/A"
                hittersStats.append(filteredStats)
        else:
            st.write(f"Player '{player_item}' not found.")

    if comparison_mode in ["Batters", "Pitchers"]:
        # Capture the expected stats df from your module and save to session state
        st.session_state.df_expected = statcast.get_stats(players, comparison_mode=comparison_mode)
        st.session_state.df_expected_mode = comparison_mode

# --- Existing Tables Output ---
if hittersStats:
    st.subheader("Hitter Statistics")
    df_hitters = pd.DataFrame(hittersStats)
    # ... your existing table styling logic ...
    st.dataframe(df_hitters) # Placeholder for your styled logic
    
if pitchersStats:
    st.subheader("Pitcher Statistics")
    df_pitchers = pd.DataFrame(pitchersStats)
    # ... your existing table styling logic ...
    st.dataframe(df_pitchers) # Placeholder for your styled logic


df_exp = st.session_state.df_expected

if df_exp is not None and not df_exp.empty:
    st.write("---")
    if st.session_state.df_expected_mode == "Pitchers":
        st.subheader("Pitcher Statcast Comparison")
    else:
        st.subheader("Batter Statcast Comparison")

    # Define realistic max caps for scaling to a 0-100 percentage layout
    baselines = {
        "est_ba": 0.360,    
        "est_slg": 0.700,   
        "est_woba": 0.460,  
        "brl_percent": 26.0,
        # Pitcher baselines for scaling (used to compute display pct)
        "xera": 6.5,
        "xba": 0.400,
        "k_pct": 40.0,
        "bb_pct": 15.0,
    }

    # Custom CSS to style inspired by Baseball Savant
    st.markdown("""
        <style>
        .stat-container {
            margin-bottom: 15px;
        }
        .stat-label {
            font-size: 14px;
            font-weight: bold;
            margin-bottom: 4px;
        }
        .stat-track {
            background-color: #e0e0e0;
            border-radius: 10px;
            width: 100%;
            height: 12px;
            position: relative;
            overflow: visible;
        }
        .half-mark{
            position: absolute;
            left: 50%;
            top: -3px;
            width: 2px;
            height: 18px;
            background-color: #333333;
            z-index: 5;
            opacity: 0.8;
        }
        @media (prefers-color-scheme: dark) {
            .half-mark {
                background-color: #FFFFFF;
            }    
        }
        .stat-bar {
            height: 100%;
            border-radius: 10px 0 0 10px;
            transition: width 0.5s ease-in-out;
        }
        .stat-bar-label {
            position: absolute;
            top: -18px;
            font-size: 12px;
            font-weight: 700;
            white-space: nowrap;
            text-shadow: 0 1px 0 rgba(0,0,0,0.4);
        }
        </style>
    """, unsafe_allow_html=True)

    # MLB-wide min/max anchors (edit these in-code to set 0th/100th anchors)
    # Format: stat -> [min, max]
    # Example: {"est_ba": [0.200, 0.400], "brl_percent": [0.0, 30.0]}
    MLB_ANCHORS = {
        # Format: [min, mean, max]
        "est_ba": [0.150, 0.246, 0.310],
        "est_slg": [0.300, 0.402, 0.575],
        "est_woba": [0.280, 0.320, 0.415],
        "brl_percent": [0.0, 7.0, 17.0],
        "xera": [2.00, 4.00, 6.00],
        "xba": [0.250, 0.320, 0.420],
        "k_pct": [0.0, 20.0, 50.0],
        "bb_pct": [0.0, 8.0, 20.0],
    }
    anchors = MLB_ANCHORS

    # Function to dynamically calculate Blue-to-Red gradient based on percentile
    def get_stat_color(pct):
        # pct ranges from 0 to 100

        if pct < 50:
            fraction = pct / 50
            r = int(0 + fraction * 150) #150
            g = int(0 + fraction * 175) #175
            b = int(255 + fraction * -55) #200
        else:
            # Fade from light blue/grey to red
            r = 255
            g = int((1 - (pct - 50) / 75) * 200)
            b = int((1 - (pct - 50) / 75) * 200)
        return f"rgb({r}, {g}, {b})"

    # Keys where a lower raw value is better (we invert the scale for display)
    lower_better_keys = {"xera", "xba", "bb_pct"}

    def get_display_pct(value, baseline, key=None):
        # Compute percentile among the displayed cohort when possible (more accurate)
        try:
            if value is None:
                return 0
            val = float(value)
        except Exception:
            return 0

        raw_pct = 0

        # If user provided MLB anchors for this key, prefer them (stable across
        # runs). Anchors should be a mapping stat -> [min, max]. Otherwise,
        # compute a linear mapping from cohort min->0 to max->100 (smoother for
        # small groups).
        if key and key in anchors:
            try:
                a = anchors[key]
                # support either [min,max] or [min,mean,max]
                if isinstance(a, (list, tuple)) and len(a) == 3:
                    amin, amean, amax = float(a[0]), float(a[1]), float(a[2])
                    if amax != amin:
                        if val <= amean:
                            raw_pct = int(np.interp(val, [amin, amean], [0, 50]))
                        else:
                            raw_pct = int(np.interp(val, [amean, amax], [50, 100]))
                    else:
                        raw_pct = 50
                elif isinstance(a, (list, tuple)) and len(a) == 2:
                    amin, amax = float(a[0]), float(a[1])
                    if amax != amin:
                        raw_pct = int(np.interp(val, [amin, amax], [0, 100]))
                    else:
                        raw_pct = 50
                else:
                    raw_pct = 0
            except Exception:
                raw_pct = 0
        elif key and key in df_exp.columns:
            try:
                series = pd.to_numeric(df_exp[key], errors="coerce").dropna()
                if not series.empty:
                    smin = float(series.min())
                    smax = float(series.max())
                    smean = float(series.mean())
                    if smax != smin:
                        # piecewise linear: min->0, mean->50, max->100
                        if val <= smean:
                            raw_pct = int(np.interp(val, [smin, smean], [0, 50]))
                        else:
                            raw_pct = int(np.interp(val, [smean, smax], [50, 100]))
                    else:
                        raw_pct = 50
                else:
                    raw_pct = 0
            except Exception:
                raw_pct = 0
        else:
            # Fallback: normalize to provided baseline cap
            try:
                base = float(baseline) if baseline else 1.0
                raw_pct = min(int((val / base) * 100), 100)
            except Exception:
                raw_pct = 0

        if st.session_state.df_expected_mode == "Pitchers" and key in lower_better_keys:
            return 100 - raw_pct
        return raw_pct

    def format_stat_value(key, val):
        # Format numeric display based on metric key
        if val is None:
            return "N/A"
        if key in ("xera",):
            return f"{val:.2f}"
        if key in ("est_ba", "est_slg", "est_woba", "xba"):
            return f".{int(val * 1000)}"
        if key.endswith("_pct"):
            try:
                return f"{val:.1f}%"
            except Exception:
                return f"{val}%"
        return str(val)

    def render_stat_html(label, display_value, pct, color):
        # Choose a text color that contrasts with the bar fill
        try:
            pct_int = int(pct)
        except Exception:
            pct_int = 0
        text_color = "#FFFFFF"

        # position the label near the bar end; clamp to track bounds
        left_pos = max(min(pct_int, 97), 3)

        return f"""
            <div class="stat-container">
                <div class="stat-label">{label}: {display_value}</div>
                <div class="stat-track">
                    <div class="stat-bar" style="width: {pct_int}%; background-color: {color};"></div>
                    <div class="stat-bar-label" style="left: {left_pos}%; color: {text_color};">{pct_int}</div>
                    <div class="half-mark"></div>
                </div>
            </div>
        """

    # Prior version attempted to support many alternate column names.
    # `statcast.get_stats()` now returns canonical columns for pitchers: `xera`, `xba`, `k_pct`, `bb_pct`, `brl_percent`.
    # We'll read those directly (using .get to avoid KeyError) rather than guessing alternates.

    num_players = len(df_exp)
    cols = st.columns(num_players)

    # Separate render paths for pitchers and batters to avoid mismatches
    if st.session_state.df_expected_mode == "Pitchers":
        for idx, (_, row) in enumerate(df_exp.iterrows()):
            with cols[idx]:
                st.markdown(f"### {row.get('player', 'Player')}")

                # xERA
                key, label = ("xera", "xERA")
                val = row.get(key, None)
                pct = get_display_pct(val, baselines.get(key, 1), key=key)
                color = get_stat_color(pct)
                display_value = format_stat_value(key, val)
                st.markdown(render_stat_html(label, display_value, pct, color), unsafe_allow_html=True)

                # xBA
                key, label = ("xba", "xBA")
                val = row.get(key, None)
                pct = get_display_pct(val, baselines.get(key, 1), key=key)
                color = get_stat_color(pct)
                display_value = format_stat_value(key, val)
                st.markdown(render_stat_html(label, display_value, pct, color), unsafe_allow_html=True)

                # K%
                key, label = ("k_pct", "K%")
                val = row.get(key, None)
                pct = get_display_pct(val, baselines.get(key, 1), key=key)
                color = get_stat_color(pct)
                display_value = format_stat_value(key, val)
                st.markdown(render_stat_html(label, display_value, pct, color), unsafe_allow_html=True)

                # BB%
                key, label = ("bb_pct", "BB%")
                val = row.get(key, None)
                pct = get_display_pct(val, baselines.get(key, 1), key=key)
                color = get_stat_color(pct)
                display_value = format_stat_value(key, val)
                st.markdown(render_stat_html(label, display_value, pct, color), unsafe_allow_html=True)
    else:
        # Batters path (existing layout)
        for idx, (_, row) in enumerate(df_exp.iterrows()):
            with cols[idx]:
                st.markdown(f"### {row.get('player', 'Player')}")

                # est_ba
                key, label = ("est_ba", "Expected AVG")
                val = row.get(key, None)
                pct = get_display_pct(val, baselines.get(key, 1), key=key)
                color = get_stat_color(pct)
                display_value = format_stat_value(key, val)
                st.markdown(render_stat_html(label, display_value, pct, color), unsafe_allow_html=True)

                # est_slg
                key, label = ("est_slg", "Expected SLG")
                val = row.get(key, None)
                pct = get_display_pct(val, baselines.get(key, 1), key=key)
                color = get_stat_color(pct)
                display_value = format_stat_value(key, val)
                st.markdown(render_stat_html(label, display_value, pct, color), unsafe_allow_html=True)

                # est_woba
                key, label = ("est_woba", "Expected wOBA")
                val = row.get(key, None)
                pct = get_display_pct(val, baselines.get(key, 1), key=key)
                color = get_stat_color(pct)
                display_value = format_stat_value(key, val)
                st.markdown(render_stat_html(label, display_value, pct, color), unsafe_allow_html=True)

                # brl_percent
                key, label = ("brl_percent", "Barrel %")
                val = row.get(key, None)
                pct = get_display_pct(val, baselines.get(key, baselines.get("brl_percent", 1)), key=key)
                color = get_stat_color(pct)
                display_value = format_stat_value(key, val)
                st.markdown(render_stat_html(label, display_value, pct, color), unsafe_allow_html=True)