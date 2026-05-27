import requests
import smtplib
from email.message import EmailMessage
from styling import build_html
import os
from dotenv import load_dotenv

load_dotenv()

EMAIL = os.getenv("EMAIL")
APP_PASSWORD = os.getenv("APP_PASSWORD")
RECIPIENTS = [email.strip() for email in os.getenv("RECIPIENTS").split(",")]

url = "https://statsapi.mlb.com/api/v1/stats/leaders"

#the categories to pull data for
categories = {
    "homeRuns": ("HR", "hitting"),
    "battingAverage": ("AVG", "hitting"),
    "onBasePlusSlugging": ("OPS", "hitting")
}

leaders_data = {}

#fetch the data
for category, (label, group) in categories.items():

    params = {
        "leaderCategories": category,
        "statGroup": group,
        "limit": 3
    }
    response = requests.get(url, params=params)
    data = response.json()
    leaders = data['leagueLeaders'][0]['leaders']
    leaders_data[label] = [
        {
            "name": player['person']['fullName'],
            "value": player['value'],
            "team": player['team']['name']
        }
        for player in leaders
    ]

# build the html for the email
html = build_html(leaders_data)

#make the actual email
# make the actual email
msg = EmailMessage()
msg['Subject'] = 'MLB League Leaders'
msg['From'] = f"MLB Bot <{EMAIL}>"
msg['To'] = ", ".join(RECIPIENTS)

msg.set_content("Your email client does not support HTML.")
msg.add_alternative(html, subtype='html')

# send email
with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
    smtp.login(EMAIL, APP_PASSWORD)
    smtp.send_message(msg, to_addrs=RECIPIENTS)

print("Email sent!")