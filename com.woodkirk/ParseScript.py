__author__ = 'iainm'

import json
import re
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from json2html import *
from collections import OrderedDict

sender_email = "woodkirkvalleyupdates@gmail.com"
receiver_email = ["wakeyowl@gmail.com", "headoffootball@woodkirkvalleyfc.org" ]
#receiver_email = ["wakeyowl@gmail.com", "headoffootball@woodkirkvalleyfc.org", "ryanhealey1984@googlemail.com", "paulgunjal@gmail.com"]
password = input("Type your password and press enter:")
ftime_date_period = "7"

fixturesurls = {
    "url_garforth_boys": "https://fulltime.thefa.com/fixtures.html?selectedSeason=137898063&selectedFixtureGroupAgeGroup=0&selectedFixtureGroupKey=&selectedDateCode=" + ftime_date_period + "days&selectedClub=655071567&selectedTeam=&selectedRelatedFixtureOption=2&selectedFixtureDateStatus=&selectedFixtureStatus=&previousSelectedFixtureGroupAgeGroup=&previousSelectedFixtureGroupKey=&previousSelectedClub=655071567&itemsPerPage=100",
    "url_hudd_boys": "https://fulltime.thefa.com/fixtures/1/100.html?selectedSeason=22218977&selectedFixtureGroupAgeGroup=0&previousSelectedFixtureGroupAgeGroup=&selectedFixtureGroupKey=&previousSelectedFixtureGroupKey=&selectedDateCode=" + ftime_date_period + "days&selectedRelatedFixtureOption=2&selectedClub=344917937&previousSelectedClub=344917937&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus=",
    "url_westriding_fa_dev_league": "https://fulltime.thefa.com/fixtures.html?selectedSeason=804066443&selectedFixtureGroupKey=&selectedDateCode=" + ftime_date_period + "days&selectedClub=784070333&selectedTeam=&selectedRelatedFixtureOption=2&selectedFixtureDateStatus=&selectedFixtureStatus=&previousSelectedFixtureGroupAgeGroup=&previousSelectedFixtureGroupKey=&previousSelectedClub=784070333&itemsPerPage=25",
    "url_west_riding_womens": "https://fulltime.thefa.com/fixtures.html?selectedSeason=188043962&selectedFixtureGroupKey=&selectedDateCode=" + ftime_date_period + "days&selectedClub=424649067&selectedTeam=&selectedRelatedFixtureOption=2&selectedFixtureDateStatus=&selectedFixtureStatus=&previousSelectedFixtureGroupAgeGroup=&previousSelectedFixtureGroupKey=&previousSelectedClub=424649067&itemsPerPage=25",
    "url_girls": "https://fulltime.thefa.com/fixtures.html?selectedSeason=494509686&selectedFixtureGroupAgeGroup=0&selectedFixtureGroupKey=&selectedDateCode="+ ftime_date_period +"days&selectedClub=563927265&selectedTeam=&selectedRelatedFixtureOption=2&selectedFixtureDateStatus=&selectedFixtureStatus=&previousSelectedFixtureGroupAgeGroup=&previousSelectedFixtureGroupKey=&previousSelectedClub=563927265&itemsPerPage=25",
    "url_mens_sat": "https://fulltime.thefa.com/fixtures/1/100.html?selectedSeason=388107578&selectedFixtureGroupAgeGroup=0&previousSelectedFixtureGroupAgeGroup=&selectedFixtureGroupKey=&previousSelectedFixtureGroupKey=&selectedDateCode="+ ftime_date_period +"days&selectedRelatedFixtureOption=2&selectedClub=192561285&previousSelectedClub=192561285&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus="

}
table_json = {}
index = 0
list_of_fixtures = []
home_fixtures = []
away_fixtures = []
three_quarter_11 = []
full_sized_11 = []
three_g = []
nine_side = []
unknown = []


def parseurl(inputurl):
    global index
    page = requests.get(inputurl)

    soup = BeautifulSoup(page.content, features="html.parser")
    # table = soup.find("class", "fixtures-table")
    table = soup.find("table")
    # table_body = table.find('tbody')
    rows = table.find_all('tr')

    # Set Pitch Size Function
    def set_pitch_size(x):
        return {
            '18': "Full Sized XI",
            '17': "Full Sized XI",
            '16': "Full Sized XI",
            '15': "Full Sized XI",
            '14': "3/4 Sized XI",
            '13': "3/4 Sized XI",
            '12': "9-Side",
            '11': "9-Side",
            '10': "7-Side",
            '9': "7-Side",
            '8': "5-Side",
            '7': "5-Side",
        }.get(x, "Unknown")

    for row in rows:
        if len(row.select('td')) > 0:
            cols = row.select('td')
            # Strip new lines and apostrophes

            fixture = OrderedDict()
            home_team_check = cols[2].text.strip(" \n \r \t")
            age_group_check = home_team_check.lower().strip("woodkirk valley orange white black u under s")
            if home_team_check.lower().startswith(("woodkirk", "morley town lfc")):
                fixture['fixtureType'] = cols[0].text.strip(" \n \r \t")
                fixture['time'] = cols[1].text.strip("\n \r \t").replace('\n', ' ')
                fixture['homeTeam'] = cols[2].text.strip(" \n \r \t")
                fixture['awayTeam'] = cols[6].text.strip(" \n \r \t")
                fixture['location'] = cols[7].text.strip(" \n \r \t")
                fixture['leagueDivision'] = cols[8].text.strip(" \n \r \t")
                fixture['notes'] = cols[9].text.strip(" \n \r \t")
                fixture['pitch'] = set_pitch_size(age_group_check)
                list_of_fixtures.append(fixture)


for key, url in fixturesurls.items():
    parseurl(url)

count = 0

# Order the dictionary based on data format ddmmyy hm
neworderdict = sorted(list_of_fixtures, key=lambda i: datetime.strptime((i['time']), "%d/%m/%y %H:%M"))

full_sized_11 = [game for game in neworderdict if game['pitch'] == "Full Sized XI"]
unknown = [game for game in neworderdict if game['pitch'] == "Unknown"]
three_quarter_11 = [game for game in neworderdict if game['pitch'] == "3/4 Sized XI"]
# List of multiple game types in list
list_keys_3_g = ["7-Side", "5-Side"]
three_g = list(filter(lambda d: d['pitch'] in list_keys_3_g, neworderdict))
nine_side = [game for game in neworderdict if game['pitch'] == "9-Side"]


def parse_dict_to_html(dict_name):

    parsestring = json.dumps(dict_name)
    output_table = json2html.convert(json=parsestring)
    output_table = re.sub(r'<table border=\"1\"><tr><th>fixtures</th><td>', "", output_table)
    output_table = re.sub(r'<table border=\"1\">',
                         "<table border=\"1\" style=\"border-collapse:collapse;width:100%;font-family:Verdana, Arial, Tahoma, Serif;\" class=\"sortable\">",
                         output_table)
    output_table = re.sub(r'<tr>', "<tr style=\"background-color:#ffad33;\">", output_table)
    output_table = re.sub(r'<th>', "<th style=\"background-color:#000000;color:white;\">", output_table)
    output_table = re.sub(r'</table></td></tr></table>', "</table>", output_table)
    return output_table


full_sized_11_html = parse_dict_to_html(full_sized_11)
three_quarter_11_html = parse_dict_to_html(three_quarter_11)
three_g_html = parse_dict_to_html(three_g)
nine_side_html = parse_dict_to_html(nine_side)
unknown_html = parse_dict_to_html(unknown)


# Email Sending
message = MIMEMultipart("alternative")
message["Subject"] = "Woodkirk Valley Home Fixtures - Next "+ftime_date_period+" days"
message["From"] = sender_email
message["To"] = ', '.join(receiver_email)

# Create the plain-text and HTML version of your message
text = """\
Woodkirk Valley Home Fixtures - Next """+ftime_date_period+""" Days"""
html = """\
<html>
  <body>
    <h1>
    <img src="https://woodkirkvalleyfc.org/wp/wp-content/uploads/cropped-cropped-cropped-cropped-cropped-imageedit_1_6657768956-2-1.png" alt="WVFC" width="50" height="50">Woodkirk Valley FC Home Fixtures
    </h1>
    <h2>Pitch 1 & 3 Games</h2>
    """ + nine_side_html + """
    <h2>Pitch 2 Games</h2>
    """ + three_quarter_11_html + """
    <h2>Pitch 4 & 5 Games</h2>
    """ + full_sized_11_html + """
    <h2>3G Games</h2>
    """ + three_g_html + """
    <h2>Senior Teams</h2>
    """ + unknown_html + """
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
