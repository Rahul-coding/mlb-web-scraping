import streamlit as st
import statsapi
import pandas as pd

player = st.text_input("Player Names", placeholder="Enter the names of players separated by commas (e.g. Aaron Judge, Chase Burns)")
playerId = 0
hittingStats = ["gamesPlayed", "runs", "doubles", "triples", "homeRuns", "strikeOuts", "baseOnBalls", "avg", "ops", "stolenBases"]
pitchingStats = ["gamesPlayed", "runs", "baseOnBalls", "strikeOuts", "avg", "era", "inningsPitched", "wins", "losses", "saves", "whip"]
lowerBetter = ["era", "whip"] #stats where a lower number is better, used for styling the dataframe

hittersStats = []
pitchersStats = []

#only run when the button is pressed to avoi overloading the api
if(st.button("Lookup Player(s)", help="Enter the names of players separated by commas (e.g. `Aaron Judge, Chase Burns`)")):
    players = player.split(",")
    
    for player in players:
        result = statsapi.lookup_player(player.strip())
        
        if(result):
            position = result[0]['primaryPosition']['code'] #get the code for the position (1 for pitcher)
            playerId = result[0]['id'] #to use to get the stats
            fullName = result[0]['fullName']

             #Pitcher stats
            if(position == "1"): 
                stats = statsapi.player_stat_data(playerId, "pitching", season="2026")
                unfilteredStats = stats['stats'][0]['stats']
                filteredStats = {"Name": fullName}
                for stat in pitchingStats:
                    if stat in unfilteredStats:
                        filteredStats[stat] = unfilteredStats[stat]
                    else:
                        filteredStats[stat] = 0
                pitchersStats.append(filteredStats)
            
            #hitter stats
            else: 
                stats = statsapi.player_stat_data(playerId, "hitting", season="2026")
                unfilteredStats = stats['stats'][0]['stats']
                filteredStats = {"Name": fullName}
                for stat in hittingStats:
                    if stat in unfilteredStats:
                        filteredStats[stat] = unfilteredStats[stat]
                    else:
                        filteredStats[stat] = "N/A"
                hittersStats.append(filteredStats)
        else:
            st.write(f"Player '{player.strip()}' not found.")

if hittersStats:
    st.subheader("Hitter Statistics")
    df_hitters = pd.DataFrame(hittersStats)
    if(len(hittersStats) > 1):       
        styled_hitters = df_hitters.style.set_properties(**{'text-align': 'center'}).apply(
            lambda column: ['color: red; font-weight: bold' if value == column.max() else '' for value in column], 
            axis=0,
            subset=hittingStats
        )
        st.dataframe(styled_hitters)
    else:
        st.dataframe(df_hitters)
    
   
if pitchersStats:
    st.subheader("Pitcher Statistics")
    df_pitchers = pd.DataFrame(pitchersStats)
    df_pitchers.index = df_pitchers.index + 1 #start index at 1 instead of 0
    if(len(pitchersStats) > 1):      
        styled_pitchers = df_pitchers.style.set_properties(**{'text-align': 'center'}).apply(
            lambda column: ['color: red; font-weight: bold' if (value ==column.max() and column.name not in lowerBetter) or (value == column.min() and column.name in lowerBetter) else '' for value in column], 
            axis=0,
            subset=pitchingStats
        )
        styled_pitchers = styled_pitchers.apply(
            lambda column: ['color: red; font-weight: bold' if (value == column.min() and column.name in lowerBetter) else '' for value in column],
            axis=0,
            subset=pitchingStats
        )       
        st.dataframe(styled_pitchers)
    else:
        st.dataframe(df_pitchers)
   
    