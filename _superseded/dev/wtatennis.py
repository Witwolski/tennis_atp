import functools, json
from regex import F
from requests_html import AsyncHTMLSession, HTMLSession
import pandas as pd
import datetime
from sqlite3 import connect
import requests
from bs4 import BeautifulSoup
import argparse
import datetime
from tabulate import tabulate
import pandas as pd
import openpyxl
import xlsxwriter
from cmath import nan
from typing import Type
import pandas as pd
import os
import csv
from pandas.core.arrays.integer import safe_cast
import sqlalchemy as sa
from sqlalchemy import create_engine
import pymssql
import time
from pathlib import Path
import msvcrt
import numpy as np
import logging
from playsound import playsound

logging.basicConfig(
    filename="elo_all_matches.log",
    level=logging.DEBUG,
    format="%(asctime)s - %(message)s",
    datefmt="%y-%m-%d %H:%M:%S",
)


username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database
)
devengine = create_engine(devconnection_uri)


async def async_get(url):
    replace_url = url.replace("overview", "player-stats")
    r = await Pool.get(replace_url, headers={"user-agent": ""})
    name = r.html.find(".player-profile-hero-name", first=True).text.replace("\n", " ")
    for row in r.html.find(".mega-table")[:-1]:
        service_games = row.find("td")[17].text
    for row in r.html.find(".mega-table"):
        return_games = row.find("td")[11].text
    return {
        "Name": name,
        **{"Service Games Won": service_games, "Return Games Won": return_games},
    }


url = "https://www.wtatennis.com/rankings/singles"

r = HTMLSession().get(url, headers={"user-agent": ""})
url_list = []
print(r.html.text)
for tag in r.html.find("rankings__cell rankings__cell--player"):
    if len(tag.absolute_links) > 1:
        temp = list(tag.absolute_links)
        if "topcourt" in temp[0]:
            url_list.append(temp[1])
        else:
            url_list.append(temp[0])

    else:
        poo = list(tag.absolute_links)
        url_list.append(poo[0])

# print(",".join(url_list))
Pool = AsyncHTMLSession()

results = Pool.run(*(functools.partial(async_get, tag) for tag in url_list))
serve_return_stats = pd.read_json(json.dumps(results, indent=2))
serve_return_stats.to_excel("serve.xlsx", index=False)
todays_matches = pd.read_sql_query(
    "Select Winner as player_1, Loser as player_2, Winner_Odds as player_1_odds, Loser_Odds as player_2_odds from Elo_AllMatches_Today",
    con=devengine,
)
combine = pd.merge(
    todays_matches, serve_return_stats, how="left", left_on="player_1", right_on="Name"
)
combine2 = pd.merge(
    combine, serve_return_stats, how="left", left_on="player_2", right_on="Name"
)
print(combine2)
# print(json.dumps(results, indent=2))
