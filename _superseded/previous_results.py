# Import necessary libraries
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import *


def get_match_data(start_date, time_now_formatted, devengine):

    # Get historical match data on hard surface between start date and yesterday
    elo_hard = pd.read_sql_query(
        f"Select DISTINCT * From Elo_AllMatches_Hard where Date > '{start_date}' and Date < '{time_now_formatted}'",
        con=devengine,
    )

    # Get historical match data on clay surface between start date and yesterday
    elo_clay = pd.read_sql_query(
        f"Select DISTINCT * From Elo_AllMatches_Clay where Date > '{start_date}' and Date < '{time_now_formatted}'",
        con=devengine,
    )

    # Get today's matches on hard surface that haven't yet been resulted
    elo_data_hard = pd.read_sql_query(
        f"Select DISTINCT * From Elo_AllMatches_Hard where Date like '{time_now_formatted}'",
        con=devengine,
    )

    # Get today's matches on clay surface that haven't yet been resulted
    elo_data_clay = pd.read_sql_query(
        f"Select DISTINCT * From Elo_AllMatches_Clay where Date like '{time_now_formatted}'",
        con=devengine,
    )

    return elo_hard, elo_clay, elo_data_hard, elo_data_clay


def get_player_record(player, opponent_rank, history, range_low, range_high, auto):
    if auto:
        opponent_rank_low = opponent_rank - range_low
        opponent_rank_high = opponent_rank + range_high
    else:
        opponent_rank_low = range_low
        opponent_rank_high = range_high

    player_history = history[
        (
            (history["Fav"] == player)
            & (
                (history["Dog_Rank"] > opponent_rank_low)
                & (history["Dog_Rank"] < opponent_rank_high)
            )
        )
        | (
            (history["Dog"] == player)
            & (
                (history["Fav_Rank"] > opponent_rank_low)
                & (history["Fav_Rank"] < opponent_rank_high)
            )
        )
    ]
    if player_history.empty == False:
        result = float(
            len(player_history[player_history["Winner"] == player])
            / len(player_history)
        )
        return result, len(player_history)
    else:
        return 0, 0


def get_filtered_data(elo_data, elo):
    result_df = pd.DataFrame()
    for _, row in elo_data.sort_values(by="Time").iterrows():
        low_limit = 50
        high_limit = 50

        fav_percent, games = get_player_record(
            row.Fav, row.Dog_Rank, elo_hard, low_limit, high_limit, True
        )
        count = 0
        while games < 10 and count < 5:
            count = count + 1
            low_limit = low_limit + 10
            high_limit = high_limit + 10
            fav_percent, games = get_player_record(
                row.Fav, row.Dog_Rank, elo_hard, low_limit, high_limit, True
            )

        low_limit = 50
        high_limit = 50
        dog_percent, games2 = get_player_record(
            row.Dog, row.Fav_Rank, elo_hard, low_limit, high_limit, True
        )
        count = 0
        while games2 < 10 and count < 5:
            count = count + 1
            low_limit = low_limit + 10
            high_limit = high_limit + 10
            dog_percent, games2 = get_player_record(
                row.Dog, row.Fav_Rank, elo_hard, low_limit, high_limit, True
            )

        if games > 4 and games2 > 4:
            temp_df = pd.DataFrame(
                {
                    "Winner": [row.Winner],
                    "Winner_Odds": [row.Winner_Odds],
                    "Fav_Odds": [row.Fav_Odds],
                    "Dog_Odds": [row.Dog_Odds],
                    "Fav": [row.Fav],
                    "Elo_Fav": [row.Elo_Fav],
                    "Fav_Record": ["{:.0%}".format(fav_percent)],
                    "Fav_Games": [games],
                    "Dog": [row.Dog],
                    "Dog_Odds": [row.Dog_Odds],
                    "Dog_Record": ["{:.0%}".format(dog_percent)],
                    "Dog_Games": [games2],
                    "fav_percent": [fav_percent],
                    "dog_percent": [dog_percent],
                    "Sex": [row.Sex],
                    "Date": [row.Date],
                }
            )
            result_df = pd.concat([result_df, temp_df])
    return result_df


# Connect to SQLite database using SQLAlchemy's create_engine
devengine = create_engine("sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db")
db = pd.DataFrame()
for x in range(0, 300):
    print(x)
    time_now = datetime.datetime.now() + relativedelta(days=-x)
    time_now_formatted = time_now.strftime("%Y-%m-%d")
    print(time_now_formatted)

    # Get the start date two years ago from today
    today = time_now
    two_years_ago = (today - datetime.timedelta(days=365 * 2)).strftime("%Y-%m-%d")

    elo_hard, elo_clay, elo_data_hard, elo_data_clay = get_match_data(
        two_years_ago, time_now_formatted, devengine
    )

    results_hard = get_filtered_data(elo_data_hard, elo_hard)
    results_clay = get_filtered_data(elo_data_clay, elo_clay)

    results_hard.to_sql("results_hard", if_exists="append", index=False, con=devengine)
    results_clay.to_sql("results_clay", if_exists="append", index=False, con=devengine)
