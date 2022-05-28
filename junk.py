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

username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database)
devengine = create_engine(devconnection_uri)

df_WTA_elo=pd.read_excel(r"C:\Users\chris\OneDrive\Documents\GitHub\tennis_atp\Elo.xlsx",sheet_name="WTA")
df_ATP_elo=pd.read_excel(r"C:\Users\chris\OneDrive\Documents\GitHub\tennis_atp\Elo.xlsx",sheet_name="ATP")

df_ATP_elo=pd.concat([df_ATP_elo,df_WTA_elo])

df_ExistingData=pd.read_sql("Select * FROM Bets_today",con=devengine)
#print(df_ATP_elo[["Player","Elo","hElo","cElo"]])

df_ExistingData=df_ExistingData.merge(df_ATP_elo,how="left",left_on="Player 1",right_on="Player")
df_ExistingData=df_ExistingData.merge(df_ATP_elo,how="left",left_on="Player 2",right_on="Player",suffixes=["_Player1","_Player2"])
df_ExistingData.to_sql("Bets_today_Elo",con=devengine,index=False)