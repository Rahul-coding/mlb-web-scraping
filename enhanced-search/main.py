import streamlit as st
import statsapi
import pandas as pd

playerId = 0
hittingStats = ["gamesPlayed", "runs", "doubles", "triples", "homeRuns", "strikeOuts", "baseOnBalls", "avg", "ops", "stolenBases"]
pitchingStats = ["gamesPlayed", "inningsPitched", "wins", "losses", "baseOnBalls", "strikeOuts", "avg", "era", "whip", "runs", "svhd", "blownSaves"]
lowerBetter = ["era", "whip", "avg"] #stats where a lower number is better, used for styling the dataframe

hittersStats = []
pitchersStats = []

#option to show help
with st.container(horizontal_alignment="right"):
    col_title, col_info = st.columns([7, 1])
        
    with col_info:
        st.button(
            "Info", 
            icon=":material/help:", 
            help="Enter the names of the players you want to look up, separated by commas. Enter multiple hitters/pitchers to compare their stats. The stats will be highlighted in red for the best performance in each category."
        )

player = st.text_input("Player Names", placeholder="Aaron Judge, Chase Burns")
  
#only run when the button is pressed to avoi overloading the api
if(st.button("Lookup Player(s)")):
    players = player.split(",")
    
    for player in players:
        result = statsapi.lookup_player(player.strip())
        
        if(result):
            position = result[0]['primaryPosition']['code'] #get the code for the position (1 for pitcher)
            playerId = result[0]['id'] #to use to get the stats
            fullName = result[0]['fullName']
            teamName = (statsapi.lookup_team(result[0]['currentTeam']['id']))[0].get('name') #get the team name to display in the stats table

             #Pitcher stats
            if(position == "1"): 
                stats = statsapi.player_stat_data(playerId, "pitching", season="2026")
                unfilteredStats = stats['stats'][0]['stats']
                filteredStats = {"Name": fullName, "Team": teamName}
                for stat in pitchingStats:
                    if(stat == "svhd"):
                        filteredStats[stat] = unfilteredStats.get('saves', 0) + unfilteredStats.get('holds', 0) #combine holds and saves into one stat for easier comparison
                    elif stat in unfilteredStats:
                        filteredStats[stat] = unfilteredStats[stat]
                    else:
                        filteredStats[stat] = 0
                pitchersStats.append(filteredStats)
            
            #hitter stats
            else: 
                stats = statsapi.player_stat_data(playerId, "hitting", season="2026")
                unfilteredStats = stats['stats'][0]['stats']
                filteredStats = {"Name": fullName, "Team": teamName}
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
   
    