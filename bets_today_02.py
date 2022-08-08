import pandas as pd
import numpy as np
from sqlalchemy import create_engine

username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database
)
devengine = create_engine(devconnection_uri)

data = pd.read_sql_query("Select distinct * FROM Elo_AllMatches_Today", con=devengine)
data["Elo_Dog"] = data.apply(
    lambda x: x["Winner"] if x["Winner"] != x["Elo_Fav"] else x["Loser"], axis=1
)
filter1 = data[
    [
        "Sex",
        "Elo_Fav",
        "Elo_Dog",
        "Elo_Fav_Odds",
        "Elo_Fav_Est_Odds",
        "Elo_Dog_Odds",
        "Elo_Dog_Est_Odds",
        "Wins",
        "Losses",
    ]
].copy()
filter1["WinsLosses_"] = filter1[["Wins", "Losses"]].max(axis=1)
filter1["WinsLosses"] = (filter1["WinsLosses_"] / 10).apply(np.floor).astype(int) * 10
filter1["Thresh"] = (filter1["Elo_Fav_Odds"] / 0.10).apply(np.ceil).astype(float) * 0.10
filter1.drop(columns=["Wins", "Losses"], inplace=True)
filter1 = filter1[(filter1["WinsLosses"].ge(20))]
filter1["Higher"] = filter1.apply(
    lambda x: "Higher" if x["Elo_Fav_Odds"] < (x["Elo_Fav_Est_Odds"]) else "Lower",
    axis=1,
)
filter1.sort_values(["Elo_Fav_Odds"], ascending=True).to_excel(
    "Bets_Today.xlsx", index=False
)
