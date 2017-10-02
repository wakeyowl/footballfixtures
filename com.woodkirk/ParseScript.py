__author__ = 'iainm'

from bs4 import BeautifulSoup
import urllib2
import lxml
import re
from datetime import datetime
from timestring import Date
from json2html import *

fixturesurls = {
    "url_garforth_boys": "http://full-time.thefa.com/ListPublicFixture.do?selectedFixtureGroupKey"
                         "=&selectedRelatedFixtureOption=2&selectedClub=655071567&selectedTeam"
                         "=&selectedFixtureDateStatus=&selectedFixtureStatus=&selectedDateCode=7days&selectednavpage1"
                         "=1&navPageNumber1=1&previousSelectedFixtureGroupKey=&previousSelectedClub=655071567"
                         "&seasonID=585273164&selectedSeason=585273164 "
    # ,
    # "url_girls":"http://full-time.thefa.com/ListPublicFixture.do?selectedFixtureGroupKey=&selectedRelatedFixtureOption=2&selectedClub=444560366&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus=&selectedDateCode=30days&previousSelectedFixtureGroupKey=&previousSelectedClub=444560366&seasonID=986432876&selectedSeason=986432876",
    # "url_steveRose":"http://full-time.thefa.com/ListPublicFixture.do?selectedFixtureGroupKey=&selectedRelatedFixtureOption=2&selectedClub=3832346&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus=&selectedDateCode=30days&selectednavpage1=1&navPageNumber1=1&previousSelectedFixtureGroupKey=&previousSelectedClub=&seasonID=131449576&selectedSeason=131449576",
    # "url_mens_sat":"http://full-time.thefa.com/ListPublicFixture.do?selectedFixtureGroupKey=&selectedRelatedFixtureOption=2&selectedClub=69544268&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus=&selectedDateCode=30days&selectednavpage1=1&navPageNumber1=1&previousSelectedFixtureGroupKey=&previousSelectedClub=&seasonID=620895215&selectedSeason=620895215",
    # "url_men_sun":"http://full-time.thefa.com/ListPublicFixture.do?selectedFixtureGroupKey=&selectedRelatedFixtureOption=2&selectedClub=675798519&selectedTeam=&selectedFixtureDateStatus=&selectedFixtureStatus=&selectedDateCode=30days&selectednavpage1=1&navPageNumber1=1&previousSelectedFixtureGroupKey=&previousSelectedClub=&seasonID=225632433&selectedSeason=225632433"

}
table_json = {}
index = 0


def parseurl(url):
    global index
    page = urllib2.urlopen(url)
    soup = BeautifulSoup(page.read(), 'lxml')
    table = soup.find('table')
    table_body = table.find('tbody')
    rows = table_body.find_all('tr')
    for row in rows:
        if len(row.select('td')) > 0:
            cols = row.select('td')
            # Strip new lines and apostrophes
            table_json[index] = {"fixtureType": str(cols[0].text.strip('\n')),
                                 "date": str(cols[1].text.strip('\n')),
                                 "homeTeam": str(cols[2].text.strip('\n')).replace('\'', ''),
                                 "awayTeam": str(cols[3].text.strip('\n')).replace('\'', ''),
                                 "location": str(cols[4].text.strip('\n')).replace('\'', ''),
                                 "leagueDivision": str(cols[5].text.strip('\n'))}
            index += 1


for key, url in fixturesurls.items():
    parseurl(url)

home_games = {}
count = 0
for row in table_json:
    if table_json[row]['location'].startswith('Woodkirk Valley'):
        print table_json[row]
        home_games[count] = table_json[row]
        count += 1

# Update the parsing of teams and special chars
parsestring = str(home_games)
# parsestring = str(table_json)
parsestring = re.sub(r'[0-9]?[0-9]: {', "{", parsestring)
parsestring = re.sub(r'(\d+)\'s', r'\1s', parsestring)
parsestring = re.sub(r'\'', "\"", parsestring)
parsestring = re.sub(r'^{', "{\"fixtures\": [ ", parsestring)
parsestring = re.sub(r'}}$', "}]}", parsestring)


print parsestring

outputtable = json2html.convert(json=parsestring)

outputtable = re.sub(r'<table border=\"1\"><tr><th>fixtures</th><td>', "", outputtable)
outputtable = re.sub(r'<table border=\"1\">', "<table border=\"1\" class=\"sortable\">", outputtable)
outputtable = re.sub(r'</table></td></tr></table>', "</table>", outputtable)
print outputtable
