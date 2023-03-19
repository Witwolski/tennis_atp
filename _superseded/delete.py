import pandas as pd
import smtplib
import datetime
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from smtplib import SMTP
import smtplib
from sqlalchemy import create_engine
import numpy as np
import logging
from playsound import playsound
import datetime
from dateutil.relativedelta import *


devengine = create_engine("sqlite:///C:/Git/tennis_atp/database/bets_sqllite.db")

combined_selection = pd.read_sql_query(
    "Select Elo_Fav, Elo_Fav_Odds,Time From Elo_AllMatches_Daily_Clay_Today",
    con=devengine,
)


time_now = datetime.datetime.now() + datetime.timedelta(minutes=0)
time_now_formatted_2 = time_now.strftime("%Y_%m_%d")
combined_selection.drop_duplicates().sort_values(by="Time").to_csv(
    "dailyx_{}.csv".format(time_now_formatted_2), index=False
)
