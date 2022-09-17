from tennisexplorer_Odds_Today import Today
from Elo_AllMatches_six_months import Elo
from sqlalchemy import create_engine
import pandas as pd
import numpy as np

devengine = create_engine("sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db")

while True:
    Today()
    Elo()
    elo_data = pd.read_sql_query(
        "Select * From Elo_AllMatches where date = '2022-09-16' and (Surface like 'Clay' or Surface like 'Hard') --and Elo_Fav_Est_Odds < 1.8",
        con=devengine,
    )
    daily_critera = ((elo_data["Elo_Fav_Odds"])).ge(2) & (
        (elo_data["Elo_Fav_Odds"]).le(2.1)
    )
    daily_critera1 = ((elo_data["Elo_Fav_Odds"])).ge(2.2) & (
        (elo_data["Elo_Fav_Odds"]).le(2.3)
    )
    daily_critera2 = ((elo_data["Elo_Fav_Odds"])).ge(2.5) & (
        (elo_data["Elo_Fav_Odds"]).le(2.6)
    )
    daily_critera3 = ((elo_data["Elo_Fav_Odds"])).ge(2.7) & (
        (elo_data["Elo_Fav_Odds"]).le(2.8)
    )
    daily_filtered_data = elo_data[
        daily_critera | daily_critera1 | daily_critera2 | daily_critera3
    ]

    played = ["Jasmine Paolini", "Juncheng Shang"]
    daily_filtered_data = daily_filtered_data[
        (daily_filtered_data["Elo_Fav"].isin(played)) == False
    ]

    print(daily_filtered_data[["Elo_Fav", "Elo_Dog", "Elo_Fav_Odds"]])
