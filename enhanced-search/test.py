from pybaseball import statcast_pitcher_expected_stats

# Pull expected stats for all qualified pitchers in 2025
data = statcast_pitcher_expected_stats(2025)

# Alternatively, set a specific minimum plate appearance threshold (e.g., 150)
data = statcast_pitcher_expected_stats(2025, 150)

# View the players, xERA, and other expected stats
print(data)