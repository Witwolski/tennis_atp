import functools, json
from regex import F
from requests_html import AsyncHTMLSession
import pandas as pd
import requests
from sqlalchemy import create_engine
import logging
import time

logging.basicConfig(
    filename="wta.log",
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


async def async_get(url, id):
    r = await Pool.get(url, headers={"user-agent": ""})

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
    }
    player_API = requests.get(
        "https://api.wtatennis.com/tennis/players/{}/year/2022".format(id),
        headers={"user-agent": ""},
    )
    player_txt = player_API.text
    player_json = json.loads(player_txt)
    if player_API.ok == False:
        return {
            "Name": None,
            **{
                "Service Games Won": "{}".format(0),
                "Return Games Won": "{}".format(0),
            },
        }
    else:
        name = player_json["player"]["fullName"]
        if "stats" in player_json:
            service_games = player_json["stats"]["service_games_won_percent"]
            return_games = player_json["stats"]["return_games_won_percent"]
        else:
            service_games = 0
            return_games = 0
        return {
            "Name": name,
            **{
                "Service Games Won": "{}".format(service_games),
                "Return Games Won": "{}".format(return_games),
            },
        }


data = pd.DataFrame()
for x in range(0, 5):

    response_API = requests.get(
        "https://api.wtatennis.com/tennis/players/ranked?page={}&pageSize=500&type=rankSingles&sort=asc&name=&metric=SINGLES&at=2022-07-22&nationality=".format(
            x
        ),
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
        },
    )

    response_txt = response_API.text
    response_json = json.loads(response_txt)
    url_list = []
    for player in response_json:
        player_fname = player["player"]["firstName"]
        player_lname = player["player"]["lastName"]
        player_id = player["player"]["id"]
        url = "https://www.wtatennis.com/players/{}/{}-{}#stats".format(
            player_id, player_fname, player_lname
        )
        url_list.append(url)

    Pool = AsyncHTMLSession()

    results = Pool.run(
        *(functools.partial(async_get, tag, tag.split("/")[4]) for tag in url_list)
    )
    serve_return_stats = pd.read_json(json.dumps(results, indent=2))
    data = pd.concat([data, serve_return_stats])

todays_matches = pd.read_sql_query(
    "Select Winner as player_1, Loser as player_2, Winner_Odds as player_1_odds, Loser_Odds as player_2_odds from Elo_AllMatches_Today",
    con=devengine,
)
combine = pd.merge(
    todays_matches, data, how="left", left_on="player_1", right_on="Name"
)
combine2 = pd.merge(combine, data, how="left", left_on="player_2", right_on="Name")
combine2[["Service Games Won_x", "Service Games Won_y"]] = combine2[
    ["Service Games Won_x", "Service Games Won_y"]
].astype(float)
filter_wta_serve = combine2[
    ((combine2["Service Games Won_x"]).ge(70))
    | ((combine2["Service Games Won_y"]).ge(70))
]

filter_wta_serve.to_excel("servers_today_womens.xlsx", index=False)
