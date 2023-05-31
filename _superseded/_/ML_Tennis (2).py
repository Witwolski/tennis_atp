import datetime
from sqlite3 import connect
import requests
from bs4 import BeautifulSoup
import argparse
import datetime
from tabulate import tabulate
import pandas as pd

import openpyxl
import xlsxwriter

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

# import xgboost as xgb


username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database
)
devengine = create_engine(devconnection_uri)


dataset = pd.read_sql_query(
    "SELECT Winner,Loser,Winner_Odds,Loser_Odds,Elo_Winner,Elo_Loser,Elo_Fav,Elo_Fav_Odds,Elo_Dog_Odds,Elo_Fav_Est_Odds,Elo_Dog_Est_Odds,Wins,Losses,LoserTotal FROM [Bets].[dbo].[Elo_AllMatches] where Elo_Fav_Odds > 1.9",
    con=devengine,
)

dataset["Winner_Elo"] = dataset.apply(
    lambda x: "EloFav" if x["Winner"] == x["Elo_Fav"] else "EloDog", axis=1
)

dataset.drop(
    columns=["Winner", "Loser", "Elo_Winner", "Elo_Loser", "Elo_Fav"], inplace=True
)

X = dataset.drop(["Winner_Elo"], axis=1)
y = dataset["Winner_Elo"]
X_train, X_test, y_train, y_test = train_test_split(X, y)
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

print("")
print("#########################")
print(" Training accuracy: {:.0%}".format(train_score))
print(" Testing accuracy:  {:.0%}".format(test_score))
print("#########################")
