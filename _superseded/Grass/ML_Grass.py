import datetime
from sqlite3 import connect
import requests
from bs4 import BeautifulSoup
import argparse
import datetime
from tabulate import tabulate
import pandas as pd
#from Tennis import *
import openpyxl
import xlsxwriter
from elotable_grass import GetElo
from cmath import nan
from typing import Type
import pandas as pd
import os
import csv
from pandas.core.arrays.integer import safe_cast
import sqlalchemy as sa
from sqlalchemy import create_engine
import pymssql
import time
from pathlib import Path
import msvcrt
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from collections import Counter
#import xgboost as xgb


username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database)
devengine = create_engine(devconnection_uri)


def ML(Surface):
    global counting
    dataset=pd.read_sql_query("Select [Player 1],[Elo Favourite],[Estimated Odds grass] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference grass], [Elo Difference Hard],RankDiff FROM Bets_yesterday_grass \
        where  date like '%' and [Estimated Odds] >1 and [Actual Odds] > 1.85 and [Actual Odds] > [Estimated Odds]  and [Actual Odds] > [Estimated Odds {}]  and Surface  like '{}'".format(Surface,Surface),con=devengine)

    prediction=pd.read_sql_query("Select [Player 1],[Elo Favourite],[Estimated Odds grass] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference grass], [Elo Difference Hard],RankDiff FROM Bets_today_grass \
        where  [Estimated Odds] >1 and [Actual Odds] > 1.85 and [Actual Odds] > [Estimated Odds]  and [Actual Odds] > [Estimated Odds {}]  and Surface  like '{}'".format(Surface,Surface),con=devengine)
    prediction1=pd.read_sql_query("Select [Player 1],[Elo Favourite],[Estimated Odds grass] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference grass], [Elo Difference Hard],RankDiff FROM Bets_today_grass \
        where [Estimated Odds] >1 and [Actual Odds] > 1.85 and [Actual Odds] > [Estimated Odds]  and [Actual Odds] > [Estimated Odds {}]  and Surface like '{}'".format(Surface,Surface),con=devengine)
    dataset=dataset.dropna()
    prediction=prediction.dropna()
    prediction1=prediction1.dropna()
    #print(prediction1)

    dataset["Player 1"]=dataset.apply(lambda x: "EloFav" if x["Player 1"]==x["Elo Favourite"] else "EloDog",axis=1)
    #dataset["Elo Difference"]=dataset.apply(lambda x: abs(x["Elo_Player1"]-x["Elo_Player2"]) if x["Player 1"]==x["Elo Favourite"] else abs(x["Elo_Player2"]-x["Elo_Player1"]) ,axis=1)
    #dataset["Elo Difference grass"]=dataset.apply(lambda x: abs(x["cElo_Player1"]-x["cElo_Player2"]) if x["Player 1"]==x["Elo Favourite"] else abs(x["cElo_Player2"]-x["cElo_Player1"]) ,axis=1)
    #dataset["Elo Difference Hard"]=dataset.apply(lambda x: abs(x["hElo_Player1"]-x["hElo_Player2"]) if x["Player 1"]==x["Elo Favourite"] else abs(x["hElo_Player2"]-x["hElo_Player1"]) ,axis=1)
    #dataset["RankDiff"]=dataset.apply(lambda x: abs(x["Rank_Player1"]-x["Rank_Player2"]) if x["Player 1"]==x["Elo Favourite"] else abs(x["Rank_Player2"]-x["Rank_Player1"]) ,axis=1)

    #for col in dataset.columns:
    #    print(col)

    dataset["Winner"]=dataset["Player 1"]
    dataset["Elo Favourite"]="EloFav"
    dataset["OddsDifference"]=abs(dataset["Odds"]-dataset["EstOdds"])
    dataset["OddsDifferenceClay"]=abs(dataset["Odds"]-dataset["EstOddsClay"])

    prediction["Player 1"]=dataset.apply(lambda x: "EloFav" if x["Player 1"]==x["Elo Favourite"] else "EloDog",axis=1)
    prediction["Elo Favourite"]="EloFav"
    prediction["OddsDifference"]=abs(prediction["Odds"]-prediction["EstOdds"])
    prediction["OddsDifferenceClay"]=abs(prediction["Odds"]-prediction["EstOddsClay"])

    prediction["Elo Difference"]=pd.to_numeric(prediction["Elo Difference"])
    prediction["Elo Difference grass"]=pd.to_numeric(prediction["Elo Difference grass"])
    prediction["Elo Difference Hard"]=pd.to_numeric(prediction["Elo Difference Hard"])
    prediction["Elo Difference"]=abs(prediction["Elo Difference"])
    prediction["Elo Difference grass"]=abs(prediction["Elo Difference grass"])
    prediction["Elo Difference Hard"]=abs(prediction["Elo Difference Hard"])
    #prediction["RankDiff"]=abs(prediction["RankDiff"])
    #print(dataset["RankDiff"])
    #dataset=dataset.drop(columns=['EstOddsClay','EstOdds','Odds',\
    #    'Player 1','Elo_Player1','Elo_Player2','cElo_Player1','cElo_Player2','gElo_Player1','gElo_Player2','hElo_Player1','hElo_Player2','Rank_Player1','Rank_Player2'])
    #dataset=dataset.drop(columns=['Elo Difference','Elo Difference grass','Elo Difference Hard','RankDiff'])
    #dataset=dataset.drop(columns=['Elo Difference','Elo Difference grass','Elo Difference Hard'])
    prediction=prediction.drop(columns=['Player 1','EstOddsClay','EstOdds','Odds'])
    #prediction=prediction.drop(columns=['Elo Difference','Elo Difference grass','Elo Difference Hard'])
    #prediction=prediction.drop(columns=['Elo Difference grass','Elo Difference Hard'])

    final_result= pd.get_dummies(dataset, prefix=['Elo Favourite'], columns=['Elo Favourite'])
    prediction_final=pd.get_dummies(prediction, prefix=['Elo Favourite'], columns=['Elo Favourite'])

    if Surface == 'Clay':
        final_result=dataset[["Winner","Elo Difference grass","Elo Difference"]]
        prediction_final=prediction[["Elo Difference grass","Elo Difference"]]
    if Surface == 'Hard':
        final_result=dataset[["Winner","Elo Difference Hard","Elo Difference"]]
        prediction_final=prediction[["Elo Difference Hard","Elo Difference"]]
    if Surface == 'grass':
        final_result=dataset[["Winner","Elo Difference grass","Elo Difference"]]
        prediction_final=prediction[["Elo Difference grass","Elo Difference"]]

    X=final_result.drop(['Winner'],axis=1)
    y=final_result['Winner']
    X_train, X_test, y_train, y_test=train_test_split(X,y,train_size=25)
    model=LogisticRegression(max_iter=100000000)
    model2=SVC()
    model2.fit(X_train,y_train)
    model.fit(X_train,y_train)
    train_score=model.score(X_train,y_train)
    train_score2=model2.score(X_train,y_train)
    test_score2=model2.score(X_test,y_test)
    test_score=model.score(X_test,y_test)
    '''
    print('')
    print('#########################')  
    print(" Training accuracy: {:.0%}".format(train_score2))
    print(" Testing accuracy:  {:.0%}".format(test_score2))
    print('#########################')
    '''
    if len(prediction1) ==0:
        return 0,''
    pred=model.predict(prediction_final)
    pred2=model2.predict(prediction_final)
    cols=["Prediction","Elo Favourite","Player1","Odds"]
    df=pd.DataFrame(columns=cols)
    List=[]
    for index,tuples in prediction1.iterrows():
        if index<len(prediction1):

            values=[pred2[index],prediction1["Elo Favourite"][index],prediction1["Player 1"][index],prediction1["Odds"][index]]
            zipped = zip(cols, values)
            a_dictionary = dict(zipped)
        # print(a_dictionary)
            List.append(a_dictionary)
            #print(pred[index],",",prediction1["Elo Favourite"][index],",",prediction1["Player 1"][index],",",prediction1["Odds"][index]) 
    df=df.append(List,True)
    #df=df[df["Odds"].ge(1.85)|df["Odds"].le(1.2)]
    #df=df[(df["Odds"].gt(1.11)&df["Odds"].le(1.2))|df["Odds"].ge(1.85)]
    df=df[df["Prediction"]=="EloFav"]
    players=[]
    if train_score2>0.5 and test_score2>0.5:# and df.empty==False:
        #print('')
        #print('              {}'.format(Surface))
        #print('************************************')
        #print(df[["Prediction","Elo Favourite","Odds"]].to_string(index=False))
        for player in df['Elo Favourite']:
            #print(player)
            players.append(player)
        #df.to_excel("today.xlsx")
        #print(train_score2,test_score2)
        #print('************************************')
        #print('')
        counting=counting+1
        return 1,players
    else:
        return 0,''
        

counting=0
players1=[]
for x in range(1,1000):
    #count=count+ML('Clay')[0]
    pl=ML('grass')[1]
    players1.append(pl)
flat_list = [item for sublist in players1 for item in sublist]
print(Counter(flat_list),counting)
print(counting)
#ML('Hard')