import requests
import json
import pandas as pd
import functools, json
from regex import F
from requests_html import AsyncHTMLSession, HTMLSession


async def async_get(url, id):
    r = await Pool.get(url, headers={"user-agent": ""})

    player_API = requests.get(
        "https://api.wtatennis.com/tennis/players/{}/year/2022".format(id)
    )
    player_txt = player_API.text
    player_json = json.loads(player_txt)
    name = player_json["player"]["fullName"]
    if "stats" in player_json:
        service_games = player_json["stats"]["service_games_won_percent"]
        return_games = player_json["stats"]["return_games_won_percent"]
    else:
        service_games = None
        return_games = None
    return {
        "Name": name,
        **{"Service Games Won": service_games, "Return Games Won": return_games},
    }


data = pd.DataFrame()
for x in range(0, 2):
    response_API = requests.get(
        "https://api.wtatennis.com/tennis/players/ranked?page={}&pageSize=500&type=rankSingles&sort=asc&name=&metric=SINGLES&at=2022-07-18&nationality=".format(
            x
        )
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
print(data)
