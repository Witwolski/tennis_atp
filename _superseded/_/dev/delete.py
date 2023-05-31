import requests
import json
import pandas as pd
import functools, json
from regex import F
from requests_html import AsyncHTMLSession, HTMLSession

player_API = requests.get("https://api.wtatennis.com/tennis/players/320832/year/2022")

player_txt = player_API.text
player_json = json.loads(player_txt)
name = player_json["player"]["fullName"]
if "stats" in player_json:
    service_games = player_json["stats"]["service_games_won_percent"]
    return_games = player_json["stats"]["return_games_won_percent"]
else:
    service_games = None
    return_games = None
