from operator import index
import pandas as pd
import os
from sqlalchemy import create_engine
import sys
import glob
import datetime
from datetime import date


files = glob.glob("./Results/*.txt")
for f in files:
    os.remove(f)
files = glob.glob("./Results/Excel/Dog/*")
for f in files:
    os.remove(f)
files = glob.glob("./Results/Excel/Fav/*")
for f in files:
    os.remove(f)

username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
dev_connection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database
)
bets_engine = create_engine(dev_connection_uri)
total_profit = 0


def sql_query(query, con):
    sql_query_df = pd.read_sql_query(query, con)
    return sql_query_df


def elo_mbm(sex, mask, after_date, grt):
    query = "Select * FROM Elo_AllMatches  where sex like '{}' and date  >= Convert(datetime, '{}' ) and surface = 'grass'".format(
        sex, after_date
    )
    elo_data = sql_query(query, bets_engine)
    elo_data = elo_data[(elo_data["Wins"].ge(grt)) | (elo_data["Losses"].ge(grt))]

    def odds_range(elo_data, thresh_high, thresh_low, mask):
        if mask == "Higher":
            filter = (
                (elo_data["Elo_Fav_Odds"] > thresh_low)
                & (elo_data["Elo_Fav_Odds"] <= thresh_high)
                & (elo_data["Elo_Fav_Est_Odds"] > elo_data["Elo_Fav_Odds"])
            )
        if mask == "Lower":
            filter = (
                (elo_data["Elo_Fav_Odds"] > thresh_low)
                & (elo_data["Elo_Fav_Odds"] <= thresh_high)
                & (elo_data["Elo_Fav_Est_Odds"] < elo_data["Elo_Fav_Odds"])
            )
        elo_data = elo_data[filter]
        return elo_data

    def range_win_percentage(elo_data, thresh_high, mask):
        global total_profit
        count = 0
        for _, row in elo_data.iterrows():
            if row["Winner"] == row["Elo_Fav"]:
                count = count + 1
        if len(elo_data.index) > 9:
            percentage = count / len(elo_data.index)
            if (percentage) > 0.4:
                games = len(elo_data.index)
                STAKE = 100
                elo_data["Profit"] = elo_data.apply(
                    lambda x: -STAKE
                    if x["Winner"] != x["Elo_Fav"]
                    else (x["Elo_Fav_Odds"] * STAKE) - STAKE,
                    axis=1,
                )
                elo_data.loc["Profit"] = elo_data.sum(axis=0)
                if elo_data["Profit"].iloc[-1] > 1:
                    results_table = [
                        {
                            "Sex": sex,
                            "Games": games,
                            "Thresh": thresh_high,
                            "WinPercent": "{:.0%}".format((count / games)),
                            "WinsLosses": grt,
                            "HigherLower": mask,
                            "FavDog": "Fav",
                            "Period": after_date,
                            "Profit": elo_data["Profit"].iloc[-1],
                        }
                    ]
                    return pd.DataFrame(results_table)

    data = pd.DataFrame()
    for y in range(1, 6):
        for x in range(-1, 10):
            thresh_high = y + (x * 0.1) + 0.1
            thresh_low = y + (x * 0.1)
            filtered_elo_data = odds_range(elo_data, thresh_high, thresh_low, mask)
            results = range_win_percentage(filtered_elo_data, thresh_high, mask)
            data = data.append(results)
    return data


def elo_mbm_dog(sex, mask, after_date, grt):
    query = "Select * FROM Elo_AllMatches  where sex like '{}' and date  >= Convert(datetime, '{}' ) and surface = 'grass'".format(
        sex, after_date
    )
    elo_data = sql_query(query, bets_engine)
    elo_data = elo_data[(elo_data["Wins"].ge(grt)) | (elo_data["Losses"].ge(grt))]

    def odds_range(elo_data, thresh_high, thresh_low, mask):
        if mask == "Higher":
            filter = (
                (elo_data["Elo_Dog_Odds"] > thresh_low)
                & (elo_data["Elo_Dog_Odds"] <= thresh_high)
                & (elo_data["Elo_Dog_Est_Odds"] > elo_data["Elo_Dog_Odds"])
            )
        if mask == "Lower":
            filter = (
                (elo_data["Elo_Dog_Odds"] > thresh_low)
                & (elo_data["Elo_Dog_Odds"] <= thresh_high)
                & (elo_data["Elo_Dog_Est_Odds"] < elo_data["Elo_Dog_Odds"])
            )
        elo_data = elo_data[filter]
        return elo_data

    def range_win_percentage(elo_data, thresh_high, mask):
        global total_profit
        count = 0
        for _, row in elo_data.iterrows():
            if row["Winner"] != row["Elo_Fav"]:
                count = count + 1
        if len(elo_data.index) > 9:
            percentage = count / len(elo_data.index)
            if (percentage) > 0.4:
                games = len(elo_data.index)
                STAKE = 100
                elo_data["Profit"] = elo_data.apply(
                    lambda x: -STAKE
                    if x["Winner"] == x["Elo_Fav"]
                    else (x["Elo_Dog_Odds"] * STAKE) - STAKE,
                    axis=1,
                )
                elo_data.loc["Profit"] = elo_data.sum(axis=0)
                if elo_data["Profit"].iloc[-1] > 1:
                    results = pd.DataFrame()
                    results_table = [
                        {
                            "Sex": sex,
                            "Games": games,
                            "Thresh": thresh_high,
                            "WinPercent": "{:.0%}".format((count / games)),
                            "WinsLosses": grt,
                            "HigherLower": mask,
                            "FavDog": "Dog",
                            "Period": after_date,
                            "Profit": elo_data["Profit"].iloc[-1],
                        }
                    ]
                    return pd.DataFrame(results_table)

    data = pd.DataFrame()
    for y in range(1, 6):
        for x in range(-1, 10):
            thresh_high = y + (x * 0.1) + 0.1
            thresh_low = y + (x * 0.1)
            filtered_elo_data = odds_range(elo_data, thresh_high, thresh_low, mask)
            results = range_win_percentage(filtered_elo_data, thresh_high, mask)
            data = data.append(results)
    return data


def str_join(*args):
    return "".join(map(str, args))


def analyze_past(df):
    data = pd.DataFrame()
    for _, row in df.iterrows():
        if row["FavDog"] == "Dog":
            for x in range(20, 100, 10):
                elo_results = elo_mbm_dog(
                    row["Sex"], row["HigherLower"], row["AfterDate"], x
                )
                data = data.append(elo_results)

        else:
            for x in range(20, 100, 10):
                elo_results = elo_mbm(
                    row["Sex"], row["HigherLower"], row["AfterDate"], x
                )
                data = data.append(elo_results)

    data.drop_duplicates(keep="first", inplace=True)
    return data


date_lastmonth = date.today() + datetime.timedelta(-30)
date_lastmonth_formatted = date_lastmonth.strftime("%Y-%m-%d")
table_definition = pd.read_csv("table_definition.csv")
table_definition["AfterDate"] = table_definition["AfterDate"].str.replace(
    "x", date_lastmonth_formatted
)
table_definition.to_csv("table_definition_.csv")
print(table_definition)
table_def_this_year = table_definition[table_definition["AfterDate"] == "2022-01-01"]
table_def_this_month = table_definition[
    table_definition["AfterDate"] == date_lastmonth_formatted
]

year_results = analyze_past(table_def_this_year)
month_results = analyze_past(table_def_this_month)
combine_results = pd.merge(
    year_results,
    month_results,
    how="left",
    left_on=["Thresh", "Sex", "FavDog", "HigherLower", "WinsLosses"],
    right_on=["Thresh", "Sex", "FavDog", "HigherLower", "WinsLosses"],
    suffixes=["", "_y"],
)
combine_results.to_excel("Analysis_grass.xlsx", index=False)
