import functools, json
from regex import F
from requests_html import AsyncHTMLSession, HTMLSession
import pandas as pd


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


url = (
    "https://www.atptour.com/en/rankings/singles/"
    "?rankDate=2022-7-18&countryCode=all&rankRange=1-400"
)

r = HTMLSession().get(url, headers={"user-agent": ""})
url_list = []
for tag in r.html.find(".player-cell-wrapper"):
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
todays_matches = pd.read_excel(
    r"C:\Users\chris\OneDrive\Documents\GitHub\tennis_atp\DailyFiltered.xlsx"
)
combine = pd.merge(
    todays_matches, serve_return_stats, how="left", left_on="Elo_Fav", right_on="Name"
)
combine2 = pd.merge(
    combine, serve_return_stats, how="left", left_on="Elo_Dog", right_on="Name"
)
print(combine2)
# print(json.dumps(results, indent=2))
