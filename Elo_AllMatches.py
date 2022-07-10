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
username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database)
devengine = create_engine(devconnection_uri)



data=pd.read_sql_query("Select distinct Surface,Date,Sex,Player_1 as Winner, Player_2 as Loser, Player_1_Odds as Winner_Odds, Player_2_Odds as Loser_Odds FROM AllMatches --where date  >= Convert(datetime, '2021-07-01' )",con=devengine)
data2=pd.read_sql_query("Select distinct Surface,Date,Sex,Player_1 as Winner, Player_2 as Loser, Player_1_Odds as Winner_Odds, Player_2_Odds as Loser_Odds FROM TodaysMatches",con=devengine)
data = pd.concat([data,data2]) 
#print(data)
#Perfom necessary cleaning of the data for our analysis. Focus on relevant columns for our analysis.
data=data.sort_values("Date")    #sort data frame by date
data["Surface"].str.replace("'b", "")    #drop the b' prefix from the Surface column
data['Winner']=data['Winner'].str.strip()    #remove leading and trailing whitespaces from names
data['Loser']=data['Loser'].str.strip()
data=data.reset_index(drop=True)

def get_elo_rankings(data):
    """
    Function that given the list on matches in chronological order, for each match, computes 
    the elo ranking of the 2 players at the beginning of the match.
    
    Parameters: data(pandas DataFrame) - DataFrame that contains needed information on tennis matches, e.g players names,
    winners, losesrs , surfaces etc
    
    Return: elo_ranking(pandas DataFrame) - DataFrame that contains the calculated Elo Ratings and the Pwin.
    
    """    
    players=list(pd.Series(list(data.Winner)+list(data.Loser)).value_counts().index)    #create list of all players
    elo=pd.Series(np.ones(len(players))*1500,index=players)    #create series with initialised elo rating for all players
    matches_played=pd.Series(np.zeros(len(players)), index=players)    #create series with players' matches initialised at 0 and updated after each match
    ranking_elo=[(1500,1500)]    #create initial elo's list
    for i in range(1,len(data)):
        w=data.iloc[i-1,:].Winner    #identify winning player
        l=data.iloc[i-1,:].Loser    #identify losing player
        elow=elo[w]
        elol=elo[l]
        matches_played_w=matches_played[w]
        matches_played_l=matches_played[l]
        pwin=1 / (1 + 10 ** ((elol - elow) / 400))    #compute prob of winner to win    
        K_win=250/((matches_played_w+5)**0.4)    #K-factor of winning player
        K_los=250/((matches_played_l+5)**0.4)   #K-factor of losing player
        new_elow=elow+K_win*(1-pwin)   #winning player new elo 
        new_elol=elol-K_los*(1-pwin)   #losing player new elo
        elo[w]=new_elow
        elo[l]=new_elol
        matches_played[w]+=1   #update total matches of players
        matches_played[l]+=1
        ranking_elo.append((elo[data.iloc[i,:].Winner],elo[data.iloc[i,:].Loser]))     

    ranking_elo=pd.DataFrame(ranking_elo,columns=["Elo_Winner","Elo_Loser"])    
    ranking_elo["Prob_Elo"]=1 / (1 + 10 ** ((ranking_elo["Elo_Loser"] - ranking_elo["Elo_Winner"]) / 400))  
    ranking_elo["Prob_Elo_Loser"]=1 / (1 + 10 ** ((ranking_elo["Elo_Winner"] - ranking_elo["Elo_Loser"]) / 400)) 
    return ranking_elo

elo_rankings = get_elo_rankings(data)
data = pd.concat([data,elo_rankings],1) 

def get_prob(a):
    '''Function that convert decimal odds to probabilities.
       Parameters: a - decimal odd (float) 
       Return: a - probability (float)
    '''
    a=1/a
    return a  
'''
winners = np.unique(data.Winner)
losers = np.unique(data.Loser)
players=list(pd.Series(list(data.Winner)+list(data.Loser)).value_counts().index) 
record = np.zeros(len(players))    #general record of players' matches
Clay_record =  np.zeros(len(players))    # Clay Record
Grass_record = np.zeros(len(players))    # Grass Record
Hard_record = np.zeros(len(players))    #Hard surface record

# %%
d = {'Player_name': players, 'record':record, 'Clay_record': Clay_record,
     'Grass_record':Grass_record,'Hard_record':Hard_record}
players_df = pd.DataFrame(data=d)

# %%
#print("The total number of players is: "+str(len(players)))

# %%
# Fill in features values for each feature
for i,row in enumerate(players_df.iterrows()):
    w = len(data[data.Winner == row[1].Player_name])
    l = len(data[data.Loser == row[1].Player_name])
    players_df.loc[i,'Total_Games'] = w + l
    players_df.loc[i,'record'] = np.true_divide(w,(w+l))    
     
    temp_df = data[data.Surface == "Clay"]
    w = len(temp_df[temp_df.Winner == row[1].Player_name])
    l = len(temp_df[temp_df.Loser == row[1].Player_name])
    players_df.loc[i,'Total_Clay_Games'] = w + l
    players_df.loc[i,'Clay_record'] = np.true_divide(w,(w+l))
    
    temp_df = data[data.Surface == 'Grass']
    w = len(temp_df[temp_df.Winner == row[1].Player_name])
    l = len(temp_df[temp_df.Loser == row[1].Player_name])
    players_df.loc[i,'Total_Grass_Games'] = w + l
    players_df.loc[i,'Grass_record'] = np.true_divide(w,(w+l))
    
    temp_df = data[data.Surface == 'Hard']
    w = len(temp_df[temp_df.Winner == row[1].Player_name])
    l = len(temp_df[temp_df.Loser == row[1].Player_name])
    players_df.loc[i,'Total_Hard_Games'] = w + l
    players_df.loc[i,'Hard_record'] = np.true_divide(w,(w+l))

# %%
players_df = players_df.loc[(players_df["Total_Games"]>15) & (players_df["Total_Grass_Games"]>3) & (players_df["Total_Hard_Games"]>3) & (players_df["Total_Clay_Games"]>3)]
'''
'''
# %%
players_df.isnull().sum()

# %% [markdown]
# - Now there are no NaNs resulted from players that had zero games in either one of the surfaces in our data

# %%
print("The total number of players that their results we examine is: " +str(len(players_df)))

# %%
hard_clay_corr = players_df['Hard_record'].corr(players_df["Clay_record"],method="pearson")
print("The correlation of players' perfomance between Hard and Clay surface is: %5.3f" %hard_clay_corr)

# %%
grass_clay_corr = players_df['Grass_record'].corr(players_df["Clay_record"],method="pearson")
print("The correlation of players' perfomance between Grass and Clay surface is: %5.3f" %grass_clay_corr)

# %%
grass_hard_corr = players_df['Grass_record'].corr(players_df["Hard_record"],method="pearson")
print("The correlation of players' perfomance between Grass and Hard surface is: %5.3f" %grass_hard_corr)
'''
'''
# %%
def get_adj_elo_rankings(data):
    """
    Function that given the list on matches in chronological order, for each match, computes 
    the elo ranking of the 2 players at the beginning of the match
    
    Paremeters: data - pandas DataFrame
    
    Return: ranking_elo - pandas DataFrame
    """    
    players=list(pd.Series(list(data.Winner)+list(data.Loser)).value_counts().index)    #create list of all players
    elo=pd.Series(np.ones(len(players))*1500,index=players)    #create series with initialised elo rating for all players
    adj_elo=pd.Series(np.ones(len(players))*1500,index=players)    #series to initialise adjusted elos
    elo_clay=pd.Series(np.ones(len(players))*1500,index=players)   #initialise clay specific elos
    elo_hard=pd.Series(np.ones(len(players))*1500,index=players)    #initialise hard specific elos
    elo_grass=pd.Series(np.ones(len(players))*1500,index=players)    #initialise grass specific elos
    matches_played=pd.Series(np.zeros(len(players)), index=players)    #create series with players' matches initialised at 0 and updated after each match
    matches_played_hard=pd.Series(np.zeros(len(players)), index=players)   #initialise number of matches in specific surfaces for players
    matches_played_clay=pd.Series(np.zeros(len(players)), index=players)
    matches_played_grass=pd.Series(np.zeros(len(players)), index=players)
    ranking_elo=[(1500,1500)]    #create initial elos list
    for i in range(1,len(data)):
        w=data.iloc[i-1,:].Winner    #identify winning player
        l=data.iloc[i-1,:].Loser    #identify losing player
        elow=elo[w]
        elol=elo[l]
        matches_played_w=matches_played[w]
        matches_played_l=matches_played[l]
        pwin=1 / (1 + 10 ** ((elol - elow) / 400))    #compute prob of winner to win    
        K_win=250/((matches_played_w+5)**0.4)    #K-factor of winning player
        K_los=250/((matches_played_l+5)**0.4)   #K-factor of losing player
        new_elow=elow+K_win*(1-pwin)   #winning player new elo 
        new_elol=elol-K_los*(1-pwin)   #losing player new elo
        elo[w]=new_elow
        elo[l]=new_elol
        matches_played[w]+=1   #update total matches of players
        matches_played[l]+=1
        surface = data.iloc[i-1,:].Surface    #identify the surface of each match
        #Grass
        if  surface == "Grass":           
            elo_grassw=elo_grass[w]
            elo_grassl=elo_grass[l]
            matches_played_grassw=matches_played_grass[w]
            matches_played_grassl=matches_played_grass[l]
            adj_elow =adj_elo[w]
            adj_elol = adj_elo[l] 
            pwin=1 / (1 + 10 ** ((adj_elol - adj_elow) / 400))    #alternate pwin given the grass-surface adgusted elos
            K_grass_win=250/((matches_played_grassw+5)**0.4)    #compute K-factor specific for Grass surface
            K_grass_los=250/((matches_played_grassl+5)**0.4)
            new_elo_grassw=elo_grassw+K_grass_win*(1-pwin)    #update surface specific elo rating 
            new_elo_grassl=elo_grassl+K_grass_los*(1-pwin)
            elo_grass[w]=new_elo_grassw
            elo_grass[l]=new_elo_grassl
            adj_elo[w]=0.5*new_elo_grassw +0.5*new_elow    #calculate new adj-elo of the players
            adj_elo[l]=0.5*new_elo_grassl +0.5*new_elol
            matches_played_grass[w]+=1    #update total matches on Hard surface for the players 
            matches_played_grass[l]+=1    
            ranking_elo.append((adj_elo[data.iloc[i,:].Winner],adj_elo[data.iloc[i,:].Loser]))
        #Hard   
        elif surface == "Hard":           
            elo_hardw=elo_hard[w]
            elo_hardl=elo_hard[l]
            matches_played_hardw=matches_played_hard[w]
            matches_played_hardl=matches_played_hard[l]
            adj_elow =adj_elo[w]
            adj_elol = adj_elo[l] 
            pwin=1 / (1 + 10 ** ((adj_elol - adj_elow) / 400))    #alternate pwin given the hard-surface adgusted elos
            K_hard_win=250/((matches_played_hardw+5)**0.4)    #compute K-factor specific for Hard surface
            K_hard_los=250/((matches_played_hardl+5)**0.4)
            new_elo_hardw=elo_hardw+K_hard_win*(1-pwin)    #update surface specific elo rating 
            new_elo_hardl=elo_hardl+K_hard_los*(1-pwin)
            elo_hard[w]=new_elo_hardw
            elo_hard[l]=new_elo_hardl
            adj_elo[w]=0.5*new_elo_hardw +0.5*new_elow    #calculate new adj-elo of the players
            adj_elo[l]=0.5*new_elo_hardl +0.5*new_elol
            matches_played_hard[w]+=1    #update total matches on Hard surface for the players 
            matches_played_hard[l]+=1    
            ranking_elo.append((adj_elo[data.iloc[i,:].Winner],adj_elo[data.iloc[i,:].Loser]))    
        #Clay    
        elif surface == "Clay":
            elo_clayw=elo_clay[w]
            elo_clayl=elo_clay[l]
            matches_played_clayw=matches_played_clay[w]
            matches_played_clayl=matches_played_clay[l]
            adj_elow=adj_elo[w]
            adj_elol=adj_elo[l]
            pwin=1 / (1 + 10 ** ((adj_elol - adj_elow) / 400))    #alternate pwin given the clay-surface adjusted elos
            K_clay_win=250/((matches_played_clayw+5)**0.4)
            K_clay_los=250/((matches_played_clayl+5)**0.4)
            new_elo_clayw=elo_clayw+K_clay_win*(1-pwin) 
            new_elo_clayl=elo_clayl+K_clay_los*(1-pwin)
            elo_clay[w]=new_elo_clayw
            elo_clay[l]=new_elo_clayl
            adj_elo[w] =0.5*new_elo_clayw+0.5*new_elow    
            adj_elo[l] = 0.5*new_elo_clayl+0.5*new_elol 
            matches_played_clay[w]+=1
            matches_played_clay[l]+=1
            ranking_elo.append((adj_elo[data.iloc[i,:].Winner],adj_elo[data.iloc[i,:].Loser]))
        #Carpet    
        else:       
            adj_elo[w]=new_elow
            adj_elo[l]=new_elol
            ranking_elo.append((adj_elo[data.iloc[i,:].Winner], adj_elo[data.iloc[i,:].Loser]))
    ranking_elo=pd.DataFrame(ranking_elo,columns=["Adj_Elo_Winner","Adj_Elo_Loser"])  
    ranking_elo["Prob_Adj_Elo"]=1 / (1 + 10 ** ((ranking_elo["Adj_Elo_Loser"] - ranking_elo["Adj_Elo_Winner"]) / 400))
    return ranking_elo

# %%
pd.set_option('display.float_format', lambda x: '%.6f' % x)    #convert to float format to avoid scientific notation

# %%
adj_elo_rankings = get_adj_elo_rankings(data)
data = pd.concat([data,adj_elo_rankings],1) 
'''



#data=data[((data["Elo_Winner"].ge(1600))|(data["Elo_Winner"].le(1400)))&((data["Elo_Loser"].ge(1600))|(data["Elo_Loser"].le(1400)))]
data['Elo_Fav']=data.apply(lambda x: x['Winner'] if x['Elo_Winner']>x['Elo_Loser'] else x['Loser'],axis=1)
#data['Adj_Elo_Fav']=data.apply(lambda x: x['Winner'] if x['Adj_Elo_Winner']>x['Adj_Elo_Loser'] else x['Loser'],axis=1)
data['Elo_Fav_Odds']=data.apply(lambda x: x['Winner_Odds'] if x['Elo_Winner']>x['Elo_Loser'] else x['Loser_Odds'],axis=1)
data['Elo_Dog_Odds']=data.apply(lambda x: x['Loser_Odds'] if x['Elo_Fav_Odds']==x['Winner_Odds'] else x['Winner_Odds'],axis=1)
#data['Adj_Elo_Fav_Odds']=data.apply(lambda x: x['Winner_Odds'] if x['Adj_Elo_Winner']>x['Adj_Elo_Loser'] else x['Loser_Odds'],axis=1)
data['Elo_Fav_Est_Odds']=data.apply(lambda x: 1/x['Prob_Elo'] if x['Elo_Fav_Odds']==x['Winner_Odds'] else 1/x['Prob_Elo_Loser'],axis=1)
data['Elo_Dog_Est_Odds']=data.apply(lambda x: 1/x['Prob_Elo_Loser'] if x['Elo_Fav_Odds']==x['Winner_Odds'] else 1/x['Prob_Elo'],axis=1)
tomorrow = datetime.datetime.now() + datetime.timedelta(days=0)
current_date = tomorrow.strftime("%Y-%m-%d")
data[['Elo_Fav_Odds','Elo_Dog_Odds','Elo_Fav_Est_Odds','Elo_Dog_Est_Odds']]=data[['Elo_Fav_Odds','Elo_Dog_Odds','Elo_Fav_Est_Odds','Elo_Dog_Est_Odds']].astype('float')
data['Wins']=data.groupby('Winner').cumcount()+1
data['Losses']=data.groupby('Loser').cumcount()+1
data2=data.copy(deep=True)
dataloser=data.copy(deep=True)
data2['Winner']=data2['Loser']
data3=pd.concat([data, data2]).sort_values('Date')
data3.reset_index(drop=True,inplace=True)
data3['WinnerTotal']=data3.groupby('Winner').cumcount()+1
data4=data3.merge(data,how='inner',left_on=['Date','Winner','Loser'],right_on=['Date','Winner','Loser'])
dataloser['Loser']=dataloser['Winner']
data9=pd.concat([data, dataloser]).sort_values('Date')
data9.reset_index(drop=True,inplace=True)
data9['LoserTotal']=data9.groupby('Loser').cumcount()+1
data=data9.merge(data4,how='inner',left_on=['Date','Winner','Loser'],right_on=['Date','Winner','Loser'])

data1=data[data['Date']!=current_date]
data1.to_sql("Elo_AllMatches",con=devengine,if_exists='replace',index=False)
data2=data[data['Date']==current_date]
data2.to_sql("Elo_AllMatches_Today",con=devengine,if_exists='replace',index=False)




