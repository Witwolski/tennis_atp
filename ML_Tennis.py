from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from collections import Counter
from sqlalchemy import create_engine
import pandas as pd

devengine = create_engine("sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db")


def ML(Surface):
    global counting
    dataset = pd.read_sql_query(
        "Select Winner, Elo_Fav,Elo_Fav_Odds, Elo_Dog_Odds, Elo_Winner, Elo_Loser FROM Elo_AllMatches where WinnerTotal > 70 and LoserTotal >70 and Elo_Fav_Odds > 1.9",
        con=devengine,
    )
    prediction = pd.read_sql_query(
        "Select  Winner,Loser,Elo_Fav, Elo_Fav_Odds ,Elo_Dog_Odds, Elo_Winner, Elo_Loser FROM Elo_AllMatches_Today where WinnerTotal > 70 and LoserTotal >70 and Elo_Fav_Odds > 1.9",
        con=devengine,
    )
    prediction1 = pd.read_sql_query(
        "Select Winner,Loser,Elo_Fav, Elo_Fav_Odds, Elo_Dog_Odds, Elo_Winner, Elo_Loser  FROM Elo_AllMatches_Today where WinnerTotal > 70 and LoserTotal >70 and Elo_Fav_Odds > 1.9",
        con=devengine,
    )
    dataset["Elo_EloFav"] = dataset.apply(
        lambda x: x["Elo_Winner"] if x["Winner"] == x["Elo_Fav"] else x["Elo_Loser"],
        axis=1,
    )
    dataset["Elo_EloDog"] = dataset.apply(
        lambda x: x["Elo_Loser"] if x["Winner"] == x["Elo_Fav"] else x["Elo_Winner"],
        axis=1,
    )
    dataset["FavDog"] = dataset.apply(
        lambda x: "EloFav" if x["Winner"] == x["Elo_Fav"] else "EloDog", axis=1
    )

    dataset.drop(
        columns=["Winner", "Elo_Winner", "Elo_Loser", "Elo_Fav"],
        inplace=True,
    )

    prediction["Elo_EloFav"] = prediction.apply(
        lambda x: x["Elo_Winner"] if x["Winner"] == x["Elo_Fav"] else x["Elo_Loser"],
        axis=1,
    )
    prediction["Elo_EloDog"] = prediction.apply(
        lambda x: x["Elo_Loser"] if x["Winner"] == x["Elo_Fav"] else x["Elo_Winner"],
        axis=1,
    )
    prediction.drop(
        columns=["Winner", "Loser", "Elo_Winner", "Elo_Loser", "Elo_Fav"], inplace=True
    )

    final_result = dataset
    prediction = prediction

    X = final_result.drop(["FavDog"], axis=1)
    y = final_result["FavDog"]
    X_train, X_test, y_train, y_test = train_test_split(X, y, train_size=25)
    model = LogisticRegression(max_iter=100000000)
    model2 = SVC()
    model2.fit(X_train, y_train)
    model.fit(X_train, y_train)
    train_score = model.score(X_train, y_train)
    train_score2 = model2.score(X_train, y_train)
    test_score2 = model2.score(X_test, y_test)
    test_score = model.score(X_test, y_test)

    print("")
    print("#########################")
    print(" Training accuracy: {:.0%}".format(train_score2))
    print(" Testing accuracy:  {:.0%}".format(test_score2))
    print("#########################")

    if len(prediction) == 0:
        return 0, ""
    pred = model.predict(prediction)
    pred2 = model2.predict(prediction)
    cols = ["Prediction", "Elo_Fav", "Elo_Fav_Odds"]
    df = pd.DataFrame(columns=cols)
    List = []
    for index, tuples in prediction1.iterrows():
        if index < len(prediction1):

            values = [
                pred2[index],
                prediction1["Elo_Fav"][index],
                prediction1["Elo_Fav"][index],
                prediction1["Elo_Fav_Odds"][index],
            ]
            zipped = zip(cols, values)
            a_dictionary = dict(zipped)
            # print(a_dictionary)
            List.append(a_dictionary)
            # print(pred[index],",",prediction1["Elo Favourite"][index],",",prediction1["Player 1"][index],",",prediction1["Odds"][index])
    df = df.append(List, True)
    # df=df[df["Odds"].ge(1.85)|df["Odds"].le(1.2)]
    # df=df[(df["Odds"].gt(1.11)&df["Odds"].le(1.2))|df["Odds"].ge(1.85)]
    df = df[df["Prediction"] == "Elo_Fav"]
    players = []
    if train_score2 > 0.5 and test_score2 > 0.5:  # and df.empty==False:
        # print('')
        # print('              {}'.format(Surface))
        # print('************************************')
        # print(df[["Prediction","Elo Favourite","Odds"]].to_string(index=False))
        for player in df["Elo_Fav"]:
            print(player)
            players.append(player)
        # df.to_excel("today.xlsx")
        # print(train_score2,test_score2)
        # print('************************************')
        # print('')
        counting = counting + 1
        return 1, players
    else:
        return 0, ""


counting = 0
players1 = []
for x in range(1, 2):
    # count=count+ML('Clay')[0]
    pl = ML("Hard")[1]
    players1.append(pl)
flat_list = [item for sublist in players1 for item in sublist]
print(Counter(flat_list), counting)
print(counting)
# ML('Hard')
