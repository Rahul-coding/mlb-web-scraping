# MLB Stats

## Player comparison feature (Legacy)
In this feature you can compare the current season stats of multiple players 
- **How to use the app**
  - type the names of the players separated by commas (e.g., `Ben Rice, Aaron Judge, Chase Burns`)
  - You will then be prompted about if each player is a batter or not
  - For the example about you would type  `y, y, n` (if you are unsure type `u`)
- **Compare players**
- You can also compare 2+ players who are all hitters or all pitchers (e.g., `Chase Burns,Paul Skenes`)
  - The player who has the highest stat (ex. avg, ops) will have that stat bolded
  - For stats where lower is better (e.g. `ERA` and `WHIP` the lower stat will be highlighted

## Player comparison feature (New)
In this feature youc an compare the current season stats of multiple players. I chose to
make a new version of this feature as the old one wasn't user friendly and hard to compar stats with
- **How to use this feature**
  - type the names of players separated by commas (e.g. `Ben Rice, Aaron Judge` and press `Lookup Player(s)`
  - If there is more than one hitter/pitcher the player with the higher/better stat will be in red/bolded
  - You can always access the app here: **[MLB stat comparison App](https://mlbstatscompare.streamlit.app)**


## Email Feature
This feature sends a daily email summary of leaders in 3 hitting categories
(*This feature is still very basic and only sends 3 batting categories*)
  - If there is a new leader in a stat a `NEW` badge will be next to their name. The old leader will be crossed out in red
 
**How they work backend**
- **Player Comparison (legacy):** This feature is powered by **Beautiful Soup** for web scraping. The player stats are compared against each other to determine the better stat. *Web scraping was chosen purely for educational purposes* 
- **Player Comparison (new):** The new version uses `streamlit` and the `statsapi` for MLB to pull data. I then use `pandas` to determine the highest/better stat in each column. I found the `statsapi` to be much easier to use than the MLB endpoint
- **Email Feature:** This feature utilizes the official **MLB API** to gather data, and uses `smtplib` and **GitHub Actions** to automate the email
