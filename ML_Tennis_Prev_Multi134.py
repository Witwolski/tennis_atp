import datetime
from random import seed
from sqlite3 import connect
import requests
from bs4 import BeautifulSoup
import argparse
import datetime
from tabulate import tabulate
import pandas as pd
from Tennis import *
import openpyxl
import xlsxwriter
from elotable import GetElo
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
#import xgboost as xgb

username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database)
devengine = create_engine(devconnection_uri)

def ML_Prev(Surface,Date,LowOdds,HighOdds):
    dataset=pd.read_sql_query("Select [Player 1],[Elo Favourite],[Estimated Odds Clay] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference Clay], [Elo Difference Hard],RankDiff FROM Bets_yesterday where Surface  like '{}'\
         and date not  like '202252x%'  and [Actual Odds] >= {} and [Actual Odds] <= {} and [Actual Odds] > [Estimated Odds] ".format(Surface,LowOdds,HighOdds),con=devengine)

    prediction=pd.read_sql_query("Select distinct [Player 1],[Elo Favourite],[Estimated Odds Clay] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference Clay], [Elo Difference Hard],RankDiff FROM Bets_yesterday where Surface  like '{}'\
        and date  like '{}%'   and [Actual Odds] >=  {} and [Actual Odds] <= {} and [Actual Odds] > [Estimated Odds] ".format(Surface,Date,LowOdds,HighOdds),con=devengine)
    prediction1=pd.read_sql_query("Select distinct [Player 1],[Elo Favourite],[Estimated Odds Clay] as EstOddsClay,[Estimated Odds] as EstOdds, [Actual Odds] as Odds \
        ,[Elo Difference], [Elo Difference Clay], [Elo Difference Hard],RankDiff FROM Bets_yesterday where Surface  like '{}'\
         and date  like '{}%' and [Actual Odds] >= {} and [Actual Odds] <= {}  and [Actual Odds] > [Estimated Odds] ".format(Surface,Date,LowOdds,HighOdds),con=devengine)
    dataset=dataset.dropna()
    prediction=prediction.dropna()
    prediction1=prediction1.dropna()

    dataset["Player 1"]=dataset.apply(lambda x: "EloFav" if x["Player 1"]==x["Elo Favourite"] else "EloDog",axis=1)

    if len(prediction1) ==0:
        return None

    dataset["Winner"]=dataset["Player 1"]
    dataset["Elo Favourite"]="EloFav"
    dataset["OddsDifference"]=abs(dataset["Odds"]-dataset["EstOdds"])
    dataset["OddsDifferenceClay"]=abs(dataset["Odds"]-dataset["EstOddsClay"])

    prediction["Player 1"]=dataset.apply(lambda x: "EloFav" if x["Player 1"]==x["Elo Favourite"] else "EloDog",axis=1)
    prediction["Elo Favourite"]="EloFav"
    prediction["OddsDifference"]=abs(prediction["Odds"]-prediction["EstOdds"])
    prediction["OddsDifferenceClay"]=abs(prediction["Odds"]-prediction["EstOddsClay"])

    prediction["Elo Difference"]=pd.to_numeric(prediction["Elo Difference"])
    prediction["Elo Difference Clay"]=pd.to_numeric(prediction["Elo Difference Clay"])
    prediction["Elo Difference Hard"]=pd.to_numeric(prediction["Elo Difference Hard"])
    prediction["Elo Difference"]=abs(prediction["Elo Difference"])
    prediction["Elo Difference Clay"]=abs(prediction["Elo Difference Clay"])
    prediction["Elo Difference Hard"]=abs(prediction["Elo Difference Hard"])
    if Surface == 'Clay':
        final_result=dataset[["Winner","EstOddsClay","EstOdds","Odds","RankDiff"]]
        prediction_final=prediction[["EstOddsClay","EstOdds","Odds","RankDiff"]]
    if Surface == 'Hard':
        final_result=dataset[["Winner","Elo Difference Hard","Elo Difference"]]
        prediction_final=prediction[["Elo Difference Hard","Elo Difference"]]

    X=final_result.drop(['Winner'],axis=1)
    y=final_result['Winner']
    X_train, X_test, y_train, y_test=train_test_split(X,y)
    check1=len(np.unique(X_train))
    check2=len(np.unique(y_train))    
    if check1 <2 or check2 < 2:
        return None
    model2=SVC()
    model2.fit(X_train,y_train)

    train_score2=model2.score(X_train,y_train)
    test_score2=model2.score(X_test,y_test)

    if train_score2 > 0.8 and test_score2 > 0.8:
        pred2=model2.predict(prediction_final)
        cols=["Prediction","Elo Favourite","Player1","Odds"]
        df=pd.DataFrame(columns=cols)
        List=[]
        for index,tuples in prediction1.iterrows():
            if index<len(prediction1):
                values=[pred2[index],prediction1["Elo Favourite"][index],prediction1["Player 1"][index],prediction1["Odds"][index]]
                zipped = zip(cols, values)
                a_dictionary = dict(zipped)
                List.append(a_dictionary)
        df=df.append(List,True)
        #df=df[(df["Odds"].gt(1)&df["Odds"].le(1.2))]
        df=df[df["Prediction"]=="EloFav"]
        countbets=len(df)
        Stake=100
        df["Profit"]=df.apply(lambda x: -Stake if x["Elo Favourite"]!=x["Player1"] else (x["Odds"]*Stake)-Stake,axis=1)
        df.loc['Profit']= df.sum(axis=0)
        print("{}   ${} Profit in {} bets".format(Surface,df["Profit"].iloc[-1],countbets))
        df.to_excel("YD.xlsx")
        return df["Profit"].iloc[-1]
   
Date=2022520
for y in range(0,12):
    Date1=Date+y
    print(Date1)
    print('_____')
    for x in range(0,10):
        #profit1=ML_Prev('Hard',Date)
        profit2=ML_Prev('Clay',Date1,1.2,1.3)
        #print(profit1+profit2)