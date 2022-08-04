import pandas as pd
import os
from sqlalchemy import create_engine
import sys
import glob

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


def elo_mbm(sex, mask, after_date):
    query = "Select * FROM Elo_AllMatches  where sex like '{}' and date  >= Convert(datetime, '{}' )".format(
        sex, after_date
    )
    elo_data = sql_query(query, bets_engine)
    elo_data = elo_data[(elo_data["Wins"].ge(40)) | (elo_data["Losses"].ge(40))]
    # elo_data=elo_data[(elo_data['WinnerTotal'].ge(30))|(elo_data['LoserTotal'].ge(30))]

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
                    print(games, " Games")
                    print(thresh_high)
                    print(elo_data["Profit"].iloc[-1])
                    print(count / games)
                    total_profit = total_profit + elo_data["Profit"].iloc[-1]
                    print()
                    elo_data.to_excel(
                        ".\\Results\\Excel\\Fav\\"
                        + str(thresh_high)
                        + "_"
                        + sex
                        + mask
                        + ".xlsx",
                        index=False,
                    )

    for y in range(1, 5):
        for x in range(-1, 10):
            thresh_high = y + (x * 0.1) + 0.1
            thresh_low = y + (x * 0.1)
            filtered_elo_data = odds_range(elo_data, thresh_high, thresh_low, mask)
            range_win_percentage(filtered_elo_data, thresh_high, mask)


def elo_mbm_dog(sex, mask, after_date):
    query = "Select * FROM Elo_AllMatches  where sex like '{}' and date  >= Convert(datetime, '{}' )".format(
        sex, after_date
    )
    elo_data = sql_query(query, bets_engine)
    elo_data = elo_data[(elo_data["Wins"].ge(40)) | (elo_data["Losses"].ge(40))]
    # elo_data=elo_data[(elo_data['WinnerTotal'].ge(30))|(elo_data['LoserTotal'].ge(30))]

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
                    print(games, " Games")
                    print(thresh_high)
                    print(elo_data["Profit"].iloc[-1])
                    print(count / games)
                    total_profit = total_profit + elo_data["Profit"].iloc[-1]
                    print()
                    elo_data.to_excel(
                        ".\\Results\\Excel\\Dog\\"
                        + str(thresh_high)
                        + "_"
                        + sex
                        + mask
                        + ".xlsx",
                        index=False,
                    )

    for y in range(1, 5):
        for x in range(-1, 10):
            thresh_high = y + (x * 0.1) + 0.1
            thresh_low = y + (x * 0.1)
            filtered_elo_data = odds_range(elo_data, thresh_high, thresh_low, mask)
            range_win_percentage(filtered_elo_data, thresh_high, mask)


def str_join(*args):
    return "".join(map(str, args))


table_definition = pd.read_csv("table_definition.csv")


for _, row in table_definition.iterrows():
    date_formatted = row["AfterDate"].replace("-", "_")
    output_filename = str_join(
        ".\\Results\\",
        row["Sex"],
        "_",
        row["FavDog"],
        "_",
        row["HigherLower"],
        "_",
        date_formatted,
        ".txt",
    )
    sys.stdout = open(output_filename, "w")
    if row["FavDog"] == "Dog":
        elo_mbm_dog(row["Sex"], row["HigherLower"], row["AfterDate"])
    else:
        elo_mbm(row["Sex"], row["HigherLower"], row["AfterDate"])
    print(total_profit)
    sys.stdout.close()
    total_profit = 0

"""
# Womens
sys.stdout = open(".\Results\Womens_Lower.txt", "w")
elo_mbm("Womens", "Lower")
print(total_profit)
sys.stdout.close()
total_profit = 0
# Womens
sys.stdout = open(".\Results\Womens_Higher.txt", "w")
elo_mbm("Womens", "Higher")
print(total_profit)
sys.stdout.close()
total_profit = 0
# Mens
sys.stdout = open(".\Results\Mens_Lower.txt", "w")
elo_mbm("Mens", "Lower")
print(total_profit)
sys.stdout.close()
total_profit = 0
# Womens
sys.stdout = open(".\Results\Mens_Higher.txt", "w")
elo_mbm("Mens", "Higher")
print(total_profit)
sys.stdout.close()
total_profit = 0

# Womens
sys.stdout = open(".\Results\Womens_Dog_Lower.txt", "w")
elo_mbm_dog("Womens", "Lower")
print(total_profit)
sys.stdout.close()
total_profit = 0
# Womens
sys.stdout = open(".\Results\Womens_Dog_Higher.txt", "w")
elo_mbm_dog("Womens", "Higher")
print(total_profit)
sys.stdout.close()
total_profit = 0

# Mens
sys.stdout = open(".\Results\Mens_Dog_Lower.txt", "w")
elo_mbm_dog("Mens", "Lower")
print(total_profit)
sys.stdout.close()
total_profit = 0
# Mens
sys.stdout = open(".\Results\Mens_Dog_Higher.txt", "w")
elo_mbm_dog("Mens", "Higher")
print(total_profit)
sys.stdout.close()
total_profit = 0
"""
