__author__ = 'iainm'

import re
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import pandas as pd
from pandas.io import json
from pandas.io.json import json_normalize
import requests
from bs4 import BeautifulSoup
from json2html import *

sender_email = "woodkirkvalleyupdates@gmail.com"
receiver_email = "iainthompsonmacdonald@gmail.com;wakeyowl@gmail.com"
password = input("Type your password and press enter:")

fixturesurls = {
    "url_garforth_boys": "https://fulltime.thefa.com/fixtures.html?selectedSeason=137898063"
                         "&selectedFixtureGroupAgeGroup=0&selectedFixtureGroupKey=&selectedDateCode=30days"
                         "&selectedClub=655071567&selectedTeam=&selectedRelatedFixtureOption=2"
                         "&selectedFixtureDateStatus=&selectedFixtureStatus=&previousSelectedFixtureGroupAgeGroup"
                         "=&previousSelectedFixtureGroupKey=&previousSelectedClub=655071567&itemsPerPage=100",
    "url_hudd_boys": "https://fulltime.thefa.com/fixtures/1/100.html?selectedSeason=22218977"
                     "&selectedFixtureGroupAgeGroup=0&previousSelectedFixtureGroupAgeGroup=&selectedFixtureGroupKey"
                     "=&previousSelectedFixtureGroupKey=&selectedDateCode=30days&selectedRelatedFixtureOption=2"
                     "&selectedClub=344917937&previousSelectedClub=344917937&selectedTeam=&selectedFixtureDateStatus"
                     "=&selectedFixtureStatus= "
    # ,
    # "url_girls":"http://full-time.thefa.com/ListPublicFixture.do?selectedFixtureGroupKey=&selectedRelatedFixtureOption=2&selectedClub=444560366&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus=&selectedDateCode=30days&previousSelectedFixtureGroupKey=&previousSelectedClub=444560366&seasonID=986432876&selectedSeason=986432876",
    # "url_steveRose":"http://full-time.thefa.com/ListPublicFixture.do?selectedFixtureGroupKey=&selectedRelatedFixtureOption=2&selectedClub=3832346&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus=&selectedDateCode=30days&selectednavpage1=1&navPageNumber1=1&previousSelectedFixtureGroupKey=&previousSelectedClub=&seasonID=131449576&selectedSeason=131449576",
    # "url_mens_sat":"http://full-time.thefa.com/ListPublicFixture.do?selectedFixtureGroupKey=&selectedRelatedFixtureOption=2&selectedClub=69544268&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus=&selectedDateCode=30days&selectednavpage1=1&navPageNumber1=1&previousSelectedFixtureGroupKey=&previousSelectedClub=&seasonID=620895215&selectedSeason=620895215",
    # "url_men_sun":"http://full-time.thefa.com/ListPublicFixture.do?selectedFixtureGroupKey=&selectedRelatedFixtureOption=2&selectedClub=675798519&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus=&selectedDateCode=30days&selectednavpage1=1&navPageNumber1=1&previousSelectedFixtureGroupKey=&previousSelectedClub=&seasonID=225632433&selectedSeason=225632433"

}
table_json = {}
index = 0


def parseurl(inputUrl):
    global index
    page = requests.get(inputUrl)

    soup = BeautifulSoup(page.content, features="html.parser")
    # table = soup.find("class", "fixtures-table")
    table = soup.find("table")
    # table_body = table.find('tbody')
    rows = table.find_all('tr')
    for row in rows:
        if len(row.select('td')) > 0:
            cols = row.select('td')
            # Strip new lines and apostrophes
            table_json[index] = {"fixtureType": cols[0].text.strip(" \n \r \t"),
                                 "time": cols[1].text.strip("\n \r \t").replace('\n', ' '),
                                 "homeTeam": cols[2].text.strip(" \n \r \t"),
                                 "awayTeam": cols[6].text.strip(" \n \r \t"),
                                 "location": cols[7].text.strip(" \n \r \t"),
                                 "leagueDivision": cols[8].text.strip(" \n \r \t"),
                                 "notes": cols[9].text.strip(" \n \r \t"),
                                 }
            index += 1


for key, url in fixturesurls.items():
    parseurl(url)

home_games = {}
count = 0
for row in table_json:
    if table_json[row]['location'].startswith('Woodkirk'):
        # print(table_json[row])
        home_games[count] = table_json[row]
        count += 1
# print(table_json)

# Update the parsing of teams and special chars
parsestring = str(home_games)
# parsestring = str(table_json)
parsestring = re.sub(r'[0-9]?[0-9]: {', "{", parsestring)
parsestring = re.sub(r'(\d+)\'s', r'\1s', parsestring)
parsestring = re.sub(r'\'', "\"", parsestring)
parsestring = re.sub(r'^{', "{\"fixtures\": [ ", parsestring)
parsestring = re.sub(r'}}$', "}]}", parsestring)

# print(parsestring)

# Parsing Json object
# json_parse = json.loads(parsestring)


outputtable = json2html.convert(json=parsestring)

outputtable = re.sub(r'<table border=\"1\"><tr><th>fixtures</th><td>', "", outputtable)
outputtable = re.sub(r'<table border=\"1\">', "<table border=\"1\" class=\"sortable\">", outputtable)
outputtable = re.sub(r'</table></td></tr></table>', "</table>", outputtable)
print(outputtable)

# Email Sending
message = MIMEMultipart("alternative")
message["Subject"] = "Woodkirk Valley Home Fixtures - Next 30 days"
message["From"] = sender_email
message["To"] = receiver_email

# Create the plain-text and HTML version of your message
text = """\
Woodkirk Valley Home Fixtures - Next 30 Days"""
html = """\
<html>
  <body>
    <p>Home Fixtures
    </p>
    """ + outputtable + """
  </body>
</html>
"""

# Turn these into plain/html MIMEText objects
part1 = MIMEText(text, "plain")
part2 = MIMEText(html, "html")

# Add HTML/plain-text parts to MIMEMultipart message
# The email client will try to render the last part first
message.attach(part1)
message.attach(part2)

# Create secure connection with server and send email
context = ssl.create_default_context()
with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
    server.login(sender_email, password)
    server.sendmail(
        sender_email, receiver_email, message.as_string()
    )
