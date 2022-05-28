import datetime
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

history=pd.read_excel('nrlresults.xlsx',sheet_name='Results')
Fixtures=pd.read_excel('nrlresults.xlsx',sheet_name='Fixtures')
history=history.drop(columns=['Home Score','Away Score'])
final_result= pd.get_dummies(history, prefix=['Home Team','Away Team'], columns=['Home Team','Away Team'])
prediction_final=pd.get_dummies(Fixtures, prefix=['Home Team','Away Team'], columns=['Home Team','Away Team'])
#final_result=history
#prediction_final=Fixtures
for col in final_result.columns:
    if col not in prediction_final.columns and col != 'Margin':
        final_result=final_result.drop(columns=[col])

#final_result=history.drop(columns=["Home Team","Away Team"])
#prediction_final=Fixtures.drop(columns=["Home Team","Away Team"])

X=final_result.drop(['Margin'],axis=1)
y=final_result['Margin']
X_train, X_test, y_train, y_test=train_test_split(X,y,test_size=50)
model=LogisticRegression(max_iter=100000000000)
model.fit(X_train,y_train)
train_score=model.score(X_train,y_train)
test_score=model.score(X_test,y_test)
print('')
print('#########################')
print(" Training accuracy: {:.0%}".format(train_score))
print(" Testing accuracy:  {:.0%}".format(test_score))
print('#########################')
pred=model.predict(prediction_final)
print(pred)