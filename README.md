# **Player comparision feature**
- In this feture you can pull up the stats of multiple players when prompted
  - type the names of the players seperatred by commas (Ben Rice, Aaron Judge, Chase Burns)
  - You will then be prompted about if each player is a batter or not
  - For the example about you would type (y, y, n)
    - if you are unsure type u
- You can also compare 2+ players who are all hitters or all pitchers
  - This will automatically happen when comparing 2+ of the same type
  - The player who has the highest stat (ex. avg, ops) will have that stat bolded

# **Email Feature**
- This feature sends you the leaders in the whole MLB in 3 batting categories, avg, ops, and hrs
  - This feature is still very basic and only sends 3 batting categories
  - The script now saves each day's top 3 to `email/daily_leaders_snapshot.json`
  - On the next run it compares today's leaders with the previous snapshot and marks any new players in the email with a `NEW` badge
 
**How they work backend**
- The player compaision feature uses beutiful soup and webscrpaing to pull current season data
  - I chose to use web scraping for this part purely for educational purposes
- The email feature uses the MLB API to gather data and smtplib+github actions to automatically send daily emails with stat leaders
