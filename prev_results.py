# %%
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import *

devengine = create_engine("sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db")

db = pd.DataFrame()
for x in range(1, 30):
    time_now = datetime.datetime.now() + relativedelta(days=-x)
    time_now_formatted = time_now.strftime("%Y-%m-%d")
    print(time_now_formatted)

    # %%
    elo_hard = pd.read_sql_query(
        f"Select DISTINCT * From Elo_AllMatches_Hard where Date > '2021-01-01' and Date < '{time_now_formatted}'",
        con=devengine,
    )

    elo_clay = pd.read_sql_query(
        f"Select DISTINCT * From Elo_AllMatches_Clay where Date > '2021-01-01' and Date < '{time_now_formatted}'",
        con=devengine,
    )

    # %% [markdown]
    #

    # %%
    elo_data_hard = pd.read_sql_query(
        f"Select DISTINCT * From Elo_AllMatches_Hard where Date like '{time_now_formatted}' --and resulted like 'True' --and Elo_Fav_Odds>1.19 --and Winner_Rank BETWEEN 1 AND 200 --and Winner_Rank<1000",
        con=devengine,
    )

    elo_data_clay = pd.read_sql_query(
        f"Select DISTINCT * From Elo_AllMatches_Clay where Date like '{time_now_formatted}' --and resulted like 'False' --and Elo_Fav_Odds>1.19",
        con=devengine,
    )

    # %%
    elo_data_hard

    # %%
    def get_player_record(player, opponent_rank, history, time, opponent, rank):
        player_history_top50 = pd.DataFrame()
        player_history_top100 = pd.DataFrame()
        player_history = pd.DataFrame()
        if opponent_rank < 50:
            player_history_top50 = history[
                (
                    ((history["Fav"] == player) & (history["Dog_Rank"] < 50))
                    | ((history["Dog"] == player) & (history["Fav_Rank"] < 50))
                )
            ]
            # if player_history_top50.empty==False and (len(player_history_top50[player_history_top50['Winner']==player])/len(player_history_top50))  > 0.5:

            # print(time,player,"Top50",len(player_history_top50))
            # print(len(player_history_top50[player_history_top50['Winner']==player])/len(player_history_top50))
        if opponent_rank < 100:
            player_history_top100 = history[
                (
                    ((history["Fav"] == player) & (history["Dog_Rank"] < 100))
                    | ((history["Dog"] == player) & (history["Fav_Rank"] < 100))
                )
            ]
            # if player_history_top100.empty==False and (len(player_history_top100[player_history_top100['Winner']==player])/len(player_history_top100))   > 0.5:
            #    print(time,player,"Top100",len(player_history_top100))
            #    print(len(player_history_top100[player_history_top100['Winner']==player])/len(player_history_top100))

        else:
            opponent_rank_low = opponent_rank - 50
            opponent_rank_high = opponent_rank + 50
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
            # if player_history.empty==False:
            #    if (len(player_history[player_history['Winner']==player])/len(player_history)) > 0.5 and len(player_history) >5:
            #        print(time,player,opponent_rank_low,opponent_rank_high,len(player_history))
            #        print(len(player_history[player_history['Winner']==player])/len(player_history))

        return player_history, player_history_top100, player_history

    # %%
    def get_player_record(player, opponent_rank, history, range_low, range_high, auto):
        if opponent_rank == None:
            opponent_rank = 1000
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

    # %%
    result_df = pd.DataFrame()
    for _, row in elo_data_hard.sort_values(by="Time").iterrows():
        low_limit = 50
        high_limit = 50

        percent, games = get_player_record(
            row.Fav, row.Dog_Rank, elo_hard, low_limit, high_limit, True
        )
        count = 0
        while games < 10 and count < 200:
            count = count + 1
            low_limit = low_limit + 10
            high_limit = high_limit + 10
            percent, games = get_player_record(
                row.Fav, row.Dog_Rank, elo_hard, low_limit, high_limit, True
            )

        low_limit = 50
        high_limit = 50
        percent2, games2 = get_player_record(
            row.Dog, row.Fav_Rank, elo_hard, low_limit, high_limit, True
        )
        count = 0
        while games2 < 5 and count < 200:
            count = count + 1
            low_limit = low_limit + 10
            high_limit = high_limit + 10
            percent2, games2 = get_player_record(
                row.Dog, row.Fav_Rank, elo_hard, low_limit, high_limit, True
            )

        if (
            True and games > 4 and games2 > 4
        ):  # and (((percent >= 0.5)&((percent2 < 0.5))) | ((percent2 >= 0.5)&((percent < 0.5)))):
            # if  (percent2 < 5)| (percent < 5):
            temp_df = pd.DataFrame(
                {
                    "Time": [row.Time],
                    "Winner": [row.Winner],
                    "Winner_Odds": [row.Winner_Odds],
                    "Fav_Odds": [row.Fav_Odds],
                    "Dog_Odds": [row.Dog_Odds],
                    "Fav": [row.Fav],
                    "Elo_Fav": [row.Elo_Fav],
                    "Fav_Record": ["{:.0%}".format(percent)],
                    "Fav_Games": [games],
                    "Dog": [row.Dog],
                    "Dog_Odds": [row.Dog_Odds],
                    "Dog_Record": ["{:.0%}".format(percent2)],
                    "Dog_Games": [games2],
                    "percent": [percent],
                    "percent2": [percent2],
                    "Sex": [row.Sex],
                    "Date": [row.Date],
                }
            )

            result_df = pd.concat([result_df, temp_df])
            # print(row.Time, row.Fav, row.Fav_Odds, row.Dog, row.Dog_Odds)
            # print(
            #    "{:.0%}".format(percent),
            #    f"({games} Games)",
            #    "{:.0%}".format(percent2),
            #    f"({games2} Games)",
            # )
    # result_df
    if result_df.empty == True:
        print("ficl")
        continue
    # %%
    serving = pd.read_excel("servers_today.xlsx")
    serving_womens = pd.read_excel("servers_today_womens.xlsx")
    if serving_womens.empty == False:
        serving = pd.concat([serving, serving_womens])
    else:
        serving = serving
    # if serving.empty==True:

    serving = serving.drop(columns="Time")
    result = pd.merge(
        result_df, serving, how="left", left_on=["Fav", "Dog"], right_on=["Fav", "Dog"]
    )  # .to_clipboard(index=False)
    result_hard = (
        result  # [((result['percent']>0.5))|((result['percent2']>0.5))].copy()
    )

    # %%
    result_df = pd.DataFrame()
    for _, row in elo_data_clay.sort_values(by="Time").iterrows():
        low_limit = 50
        high_limit = 50

        percent, games = get_player_record(
            row.Fav, row.Dog_Rank, elo_clay, low_limit, high_limit, True
        )
        count = 0
        while games < 10 and count < 200:
            count = count + 1
            low_limit = low_limit + 10
            high_limit = high_limit + 10
            percent, games = get_player_record(
                row.Fav, row.Dog_Rank, elo_clay, low_limit, high_limit, True
            )

        low_limit = 50
        high_limit = 50
        percent2, games2 = get_player_record(
            row.Dog, row.Fav_Rank, elo_clay, low_limit, high_limit, True
        )
        count = 0
        while games2 < 5 and count < 200:
            count = count + 1
            low_limit = low_limit + 10
            high_limit = high_limit + 10
            percent2, games2 = get_player_record(
                row.Dog, row.Fav_Rank, elo_clay, low_limit, high_limit, True
            )

        if (
            True and games > 4 and games2 > 4
        ):  # and (((percent >= 0.5)&((percent2 < 0.5))) | ((percent2 >= 0.5)&((percent < 0.5)))):
            # if  (percent2 < 5)| (percent < 5):
            temp_df = pd.DataFrame(
                {
                    "Time": [row.Time],
                    "Winner": [row.Winner],
                    "Winner_Odds": [row.Winner_Odds],
                    "Fav_Odds": [row.Fav_Odds],
                    "Dog_Odds": [row.Dog_Odds],
                    "Fav": [row.Fav],
                    "Elo_Fav": [row.Elo_Fav],
                    "Fav_Record": ["{:.0%}".format(percent)],
                    "Fav_Games": [games],
                    "Dog": [row.Dog],
                    "Dog_Odds": [row.Dog_Odds],
                    "Dog_Record": ["{:.0%}".format(percent2)],
                    "Dog_Games": [games2],
                    "percent": [percent],
                    "percent2": [percent2],
                    "Sex": [row.Sex],
                    "Date": [row.Date],
                }
            )

            result_df = pd.concat([result_df, temp_df])
            # print(row.Time, row.Fav, row.Fav_Odds, row.Dog, row.Dog_Odds)
            # print(
            #    "{:.0%}".format(percent),
            #    f"({games} Games)",
            #    "{:.0%}".format(percent2),
            #    f"({games2} Games)",
            # )
    result_df

    # %%
    serving = pd.read_excel("servers_today.xlsx")
    serving_womens = pd.read_excel("servers_today_womens.xlsx")
    serving = pd.concat([serving, serving_womens])
    serving = serving.drop(columns="Time")
    result_clay = result_df
    if result_df.empty == False:
        result = pd.merge(
            result_df,
            serving,
            how="left",
            left_on=["Fav", "Dog"],
            right_on=["Fav", "Dog"],
        )  # .to_clipboard(index=False)
        result[(result["Fav_Serve%"] > 69) | (result["Dog_Serve%"] > 69)]
        clay = result
    else:
        clay2 = result_df
        clay2

    # %%
    elo_hard = pd.read_sql_query(
        f"Select DISTINCT * From Elo_AllMatches_Hard where Date > '2022-01-01' and Date < '{time_now_formatted}' --and Fav_odds>1.2 and Fav_odds<1.4 ",
        con=devengine,
    )
    winner_dataset = elo_hard[["Date", "Winner", "Winner_Odds"]].copy()
    winner_dataset["Player"] = winner_dataset["Winner"]
    winner_dataset["Odds"] = winner_dataset["Winner_Odds"]
    winner_dataset["Win/Loss"] = "Win"
    loser_dataset = elo_hard[["Date", "Loser", "Loser_Odds"]].copy()
    loser_dataset["Player"] = loser_dataset["Loser"]
    loser_dataset["Odds"] = loser_dataset["Loser_Odds"]
    loser_dataset["Win/Loss"] = "Loss"
    winner_dataset.drop(columns=["Winner", "Winner_Odds"], inplace=True)
    loser_dataset.drop(columns=["Loser", "Loser_Odds"], inplace=True)
    data_concat = pd.concat([winner_dataset, loser_dataset])
    data_concat = data_concat.sort_index()
    data_concat["Odds"] = data_concat.Odds.astype(float)

    # %%
    for _, matchup in result_hard.iterrows():
        player1 = matchup.Fav
        player2 = matchup.Dog
        player1_odds = float(matchup.Fav_Odds)
        player1_odds_hi = player1_odds + 0.2
        player1_odds_lo = 1
        player2_odds = float(matchup.Dog_Odds)
        player2_odds_hi = player2_odds + 0.5
        player2_odds_lo = 2
        player1 = data_concat[data_concat["Player"] == player1].copy()
        # player1['Streak'] = player1['Win/Loss'].groupby((player1['Win/Loss'] != player1['Win/Loss'].shift()).cumsum()).cumcount() + 1
        # player1['Streak']=player1.apply(lambda x: 'W'+str(x['Streak']) if x['Win/Loss']=='Win' else 'L'+str(x['Streak']),axis=1)
        # player1[player1['Odds']<1.4].tail(20)
        player2 = data_concat[data_concat["Player"] == player2].copy()
        # player2['Streak'] = player2['Win/Loss'].groupby((player2['Win/Loss'] != player2['Win/Loss'].shift()).cumsum()).cumcount() + 1
        # player2['Streak']=player2.apply(lambda x: 'W'+str(x['Streak']) if x['Win/Loss']=='Win' else 'L'+str(x['Streak']),axis=1)
        # player2[player2['Odds']>2.5].tail(20)
        player2 = player2[
            (player2["Odds"] > player2_odds_lo) & (player2["Odds"] < player2_odds_hi)
        ]
        if len(player2) > 0:
            winperc2 = len(player2[player2["Win/Loss"] == "Win"]) / len(player2)
        else:
            winperc2 = 0
        player1 = player1[
            (player1["Odds"] > player1_odds_lo) & (player1["Odds"] < player1_odds_hi)
        ]
        if len(player1) > 0:
            winperc1 = len(player1[player1["Win/Loss"] == "Win"]) / len(player1)
        else:
            winperc1 = 0
        if len(player1) > 5 and len(player2) > 3:
            """
            print(
                matchup.Time,
                f"{matchup.Fav} ({round(player1_odds_lo,2)}-->{round(player1_odds_hi,2)})",
                f"{matchup.Dog} ({round(player2_odds_lo,2)}-->{round(player2_odds_hi,2)})",
            )
            """
            # print(,matchup.Dog)
            # print(len(player1), winperc1, len(player2), winperc2)

    # %%
    # result_hard[result_hard['percent2']>0.5]
    """
    result_hard[
        ((result_hard["Fav_Serve%"] > 75) | (result_hard["Dog_Serve%"] > 75))
        & (result_hard["percent2"] < 0.5)
    ]
    data = result_hard[
        (result_hard["percent2"] > 0.5) & ((result_hard["percent"] < 0.5))
    ]
    """
    db = pd.concat([db, result_hard])

    db.to_sql("results_hard", con=devengine, index=False, if_exists="append")

    # db = pd.concat([db, result_clay])

    # db.to_sql("results_clay1", con=devengine, index=False, if_exists="append")
