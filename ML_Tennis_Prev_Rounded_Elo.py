from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from collections import Counter
from sqlalchemy import create_engine
import pandas as pd
import numpy as np
import datetime
from dateutil.relativedelta import *

devengine = create_engine("sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db")


def ML(tomorrow, month_ago, six_months_ago, yesterday):
    dataset = pd.read_sql_query(
        "Select Winner, Elo_Fav, Elo_Dog, Elo_Fav_Odds, Elo_Dog_Odds, Elo_Fav_Elo, Elo_Dog_Elo FROM Elo_AllMatches \
        where  date >= '{}' and date <='{}'".format(
            six_months_ago, month_ago
        ),
        con=devengine,
    )
    print("Training Data Range: {} --> {}".format(six_months_ago, yesterday))

    prediction = pd.read_sql_query(
        "Select Winner, Elo_Fav, Elo_Dog, Elo_Fav_Odds, Elo_Dog_Odds, Elo_Fav_Elo, Elo_Dog_Elo FROM Elo_AllMatches where  date > '{}'".format(
            month_ago
        ),
        con=devengine,
    )

    prediction1 = pd.read_sql_query(
        "Select Date, Winner,Elo_Fav, Elo_Dog, Elo_Fav_Odds, Elo_Dog_Odds, Elo_Fav_Elo, Elo_Dog_Elo FROM Elo_AllMatches where  date > '{}'".format(
            month_ago
        ),
        con=devengine,
    )

    dataset["Winner"] = dataset.apply(
        lambda x: "EloFav" if x["Winner"] == x["Elo_Fav"] else "EloDog", axis=1
    )

    dataset["Odds_Difference"] = dataset["Elo_Fav_Odds"] - dataset["Elo_Dog_Odds"]
    dataset["Elo_Difference"] = dataset["Elo_Fav_Elo"] - dataset["Elo_Dog_Elo"]

    dataset = dataset[
        [
            "Winner",
            "Elo_Fav_Elo",
            "Elo_Fav_Odds",
        ]
    ]
    # my_list = ["EloFav", "EloDog"]
    # dataset["Player_1"] = np.random.choice(my_list, len(dataset))
    # dataset["Player_2"] = dataset.apply(
    #    lambda x: "EloDog" if x["Player_1"] == "EloFav" else "EloFav", axis=1
    # )

    prediction["Odds_Difference"] = (
        prediction["Elo_Fav_Odds"] - prediction["Elo_Dog_Odds"]
    )

    prediction["Elo_Difference"] = prediction["Elo_Fav_Elo"] - prediction["Elo_Dog_Elo"]
    prediction = prediction[
        [
            "Elo_Fav_Elo",
            "Elo_Fav_Odds",
        ]
    ]

    final_result = dataset

    X = final_result.drop(["Winner"], axis=1)
    y = final_result["Winner"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33)
    # model = LogisticRegression(max_iter=20000000)
    model2 = SVC()
    model2.fit(X_train, y_train)
    # model.fit(X_train, y_train)
    # train_score = model.score(X_train, y_train)
    train_score2 = model2.score(X_train, y_train)
    test_score2 = model2.score(X_test, y_test)
    # test_score = model.score(X_test, y_test)

    if len(prediction) == 0:
        return 0, ""
    # pred = model.predict(prediction)
    pred2 = model2.predict(prediction)
    cols = [
        "Date",
        "Prediction",
        "Winner",
        "Elo_Fav",
        "Elo_Fav_Odds",
        "Elo_Dog",
        "Elo_Dog_Odds",
        # "Training_Accuracy",
        # "Testing_Accuracy",
    ]
    df = pd.DataFrame(columns=cols)
    List = []
    for index, tuples in prediction1.iterrows():
        if index < len(prediction1):

            values = [
                prediction1["Date"][index],
                pred2[index],
                prediction1["Winner"][index],
                prediction1["Elo_Fav"][index],
                prediction1["Elo_Fav_Odds"][index],
                prediction1["Elo_Dog"][index],
                prediction1["Elo_Dog_Odds"][index],
                #  "{:.0%}".format(train_score2),
                #  "{:.0%}".format(test_score2),
            ]
            zipped = zip(cols, values)
            a_dictionary = dict(zipped)
            List.append(a_dictionary)
    temp = pd.DataFrame(List)
    df = pd.concat([df, temp])
    df = df[df["Prediction"] == "EloFav"]
    players = []
    if train_score2 > 0.6 and test_score2 > 0.5:
        print(train_score2, test_score2)
        # print(test_score2)
        for _, i in df.iterrows():
            players.append(i)
        return 1, players
    else:
        return 0, ""


def drop_table_data(engine, table):
    devengine = create_engine(engine)
    connection = devengine.connect()
    connection.execute("Delete FROM {}".format(table))


database = "sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db"
db_table = "Predictions_Past_two_four_odds_rounded_elofav_elo"
drop_table_data(database, db_table)


for day in range(0, 60):
    date_today = datetime.datetime.now() + relativedelta(days=-day)
    date_yesterday = date_today + relativedelta(days=-1)
    date_tomorrow = date_today + relativedelta(days=1)
    date_month_ago = date_today + relativedelta(months=-1)
    date_six_months_ago = date_today + relativedelta(months=-6)
    date_tomorrow_formatted = date_tomorrow.strftime("%Y-%m-%d")
    date_yesterday_formatted = date_yesterday.strftime("%Y-%m-%d")
    date_today_formatted = date_today.strftime("%Y-%m-%d")
    date_six_months_ago_formatted = date_six_months_ago.strftime("%Y-%m-%d")
    date_month_ago_formatted = date_month_ago.strftime("%Y-%m-%d")
    print(date_today_formatted)

    players1 = []
    for x in range(1, 2):
        pl = ML(
            date_tomorrow_formatted,
            date_month_ago_formatted,
            date_six_months_ago,
            date_yesterday_formatted,
        )[1]
        players1.append(pl)
    flat_list = [item for sublist in players1 for item in sublist]
    x = pd.DataFrame(flat_list)
    x = (
        x.groupby(x.columns.tolist())
        .size()
        .reset_index()
        .rename(columns={0: "records"})
    )
    # x = x[(x["records"].ge(2)) & (x["records"].le(4))]
    if x.empty == False:
        x = x[x["Date"].str.contains(date_today_formatted)]
        if x.empty == False:
            # print(x)
            x = x[
                [
                    "Date",
                    "Winner",
                    "Elo_Fav",
                    "Elo_Fav_Odds",
                    "Elo_Dog_Odds",
                    "Elo_Dog",
                    "records",
                ]
            ]

            x = x[
                [
                    "Date",
                    "Elo_Fav",
                    "Elo_Fav_Odds",
                    "Elo_Dog_Odds",
                    "Winner",
                    "Elo_Dog",
                    "records",
                ]
            ]
            x.rename(
                columns={
                    "Elo_Fav": "Selection",
                    "Elo_Fav_Odds": "Odds",
                    "Elo_Dogs_Odds": "Opponent_Odds",
                },
                inplace=True,
            )
            x["Date"] = pd.to_datetime(x["Date"], format="%Y-%m-%d")
            x["Date"] = x["Date"].dt.strftime("%Y-%m-%d")

            x.to_sql(
                "Predictions_Past_two_four_odds_rounded_elofav_elo",
                con=devengine,
                if_exists="append",
                index=False,
            )
