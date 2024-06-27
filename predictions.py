import pandas as pd
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import datetime


def Predictions(surface):
    odds_filter = 1.7
    devengine = create_engine("sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db")
    time_now = datetime.datetime.now()
    time_now_formatted = time_now.strftime("%Y-%m-%d")
    date = time_now.date()
    past_data = pd.read_sql_query(
        f"Select distinct * from results_{surface}_1 where date < '2024-04-01'",
        con=devengine,
    )
    data = pd.read_sql_query(
        f"Select distinct * from results_{surface}_1 --where date > '2024-03-01'",
        con=devengine,
    )
    data["Fav_Odds"] = data.Fav_Odds.astype(float)
    data["Dog_Odds"] = data.Dog_Odds.astype(float)
    data["Fav_Win"] = data["Winner"] == data["Fav"]
    dog_data = data[data["Fav_Odds"] >= odds_filter].copy()
    fav_data = data[(data["Fav_Odds"] >= 1.1) & (data["Fav_Odds"] <= 1.3)].copy()

    dog_data["fav_percent_adj"] = np.ceil(dog_data["fav_percent"] * 10) / 10
    dog_data["dog_percent_adj"] = np.ceil(dog_data["dog_percent"] * 10) / 10

    fav_data["fav_percent_adj"] = np.ceil(fav_data["fav_percent"] * 10) / 10
    fav_data["dog_percent_adj"] = np.ceil(fav_data["dog_percent"] * 10) / 10

    dog_result = (
        dog_data.groupby(["fav_percent_adj", "dog_percent_adj"])["Fav_Win"]
        .agg(["mean", "count"])
        .reset_index()
    )
    dog_result.rename(
        columns={"mean": "Fav_Win_Percentage", "count": "Match_Count"}, inplace=True
    )
    dog_result.sort_values(by="Fav_Win_Percentage").to_pickle(
        f"Fav_Win_Percentage_Dog_{surface}"
    )

    fav_result = (
        fav_data.groupby(["fav_percent_adj", "dog_percent_adj"])["Fav_Win"]
        .agg(["mean", "count"])
        .reset_index()
    )
    fav_result.rename(
        columns={"mean": "Fav_Win_Percentage", "count": "Match_Count"}, inplace=True
    )
    fav_result.sort_values(by="Fav_Win_Percentage").to_pickle(
        f"Fav_Win_Percentage_Fav_{surface}"
    )

    # %%
    Fav_Win_Percentage = pd.read_pickle(f"Fav_Win_Percentage_Fav_{surface}")
    devengine = create_engine("sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db")
    hard_today = pd.read_pickle(f".\{surface}_Today")
    hard_today["fav_percent_adj"] = np.ceil(hard_today["fav_percent"] * 10) / 10
    hard_today["dog_percent_adj"] = np.ceil(hard_today["dog_percent"] * 10) / 10
    hard_today_win_percent = pd.merge(
        hard_today,
        Fav_Win_Percentage,
        left_on=["fav_percent_adj", "dog_percent_adj"],
        right_on=["fav_percent_adj", "dog_percent_adj"],
    )
    hard_today_win_percent["Date"] = date
    hard_today_win_percent = hard_today_win_percent[
        [
            "Date",
            "Time",
            "Fav_Win_Percentage",
            "Fav",
            "Fav_Odds",
            "fav_percent",
            "dog_percent",
            "Dog",
            "Dog_Odds",
        ]
    ][
        (hard_today_win_percent["Fav_Odds"] < 1.3)
        & (hard_today_win_percent["Fav_Win_Percentage"] > 0.8)
    ].sort_values(
        by=["Time"], ascending=True
    )
    hard_today_win_percent.to_csv(f"Fav_{surface}.csv", index=False)

    # %%
    Fav_Win_Percentage = pd.read_pickle(f"Fav_Win_Percentage_Dog_{surface}")
    devengine = create_engine("sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db")
    hard_today = pd.read_pickle(f".\{surface}_Today")
    hard_today["fav_percent_adj"] = np.ceil(hard_today["fav_percent"] * 10) / 10
    hard_today["dog_percent_adj"] = np.ceil(hard_today["dog_percent"] * 10) / 10
    hard_today_win_percent = pd.merge(
        hard_today,
        Fav_Win_Percentage,
        left_on=["fav_percent_adj", "dog_percent_adj"],
        right_on=["fav_percent_adj", "dog_percent_adj"],
    )
    hard_today_win_percent["Date"] = date
    hard_today_win_percent = hard_today_win_percent[
        [
            "Date",
            "Time",
            "Fav_Win_Percentage",
            "Fav",
            "Fav_Odds",
            "fav_percent",
            "dog_percent",
            "Dog",
            "Dog_Odds",
        ]
    ][
        (hard_today_win_percent["Fav_Odds"] > 1.7)
        & (hard_today_win_percent["Fav_Win_Percentage"] < 0.6)
        & (hard_today_win_percent["dog_percent"] >= 0.5)
    ].sort_values(
        by=["Time"], ascending=True
    )

    hard_today_win_percent.to_csv(f"Dog_{surface}.csv", index=False)
