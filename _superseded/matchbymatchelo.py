
from dataclasses import replace
import pandas as pd
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database)
devengine = create_engine(devconnection_uri)

path = os.getcwd()
files = os.listdir(r"C:\Users\chris\OneDrive\Documents\GitHub\tennis_atp")
files_xls = [f for f in files if f.endswith('2022.csv')]

# %%
#create empty dataframe
data=pd.DataFrame()

# %%
#extract and append data into the created empty dataframe
for f in files_xls:
    raw_data = pd.read_csv(f)
    data = data.append(raw_data)

data=pd.read_sql_query("Select [Date],len([Date]) as LenDate, [Player 1] as Winner, [Player 2] as Loser, [Actual Odds] as Odds,[Surface] from Bets_Yesterday order by len([date]) desc,[date] asc",con=devengine)
dailydata=pd.read_sql_query("Select [Date],len([Date]) as LenDate, [Player 1] as Winner, [Player 2] as Loser, [Actual Odds] as Odds,[Surface] from Bets_Today order by len([date]) desc,[date] asc",con=devengine)
data=data.append(dailydata)
data.reset_index(inplace=True, drop=True)

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


    return ranking_elo

# %%
elo_rankings = get_elo_rankings(data)
data = pd.concat([data,elo_rankings],1) 
#print(data)

# %%
#print(data[["Elo_Winner", "Elo_Loser", "Prob_Elo"]])


# %% [markdown]
# # Correlation of Players' Perfomances on Different Surfaces

# %% [markdown]
# - In this we will calculate the correlation of the perfomance of players between tha three main surfaces: Grass, Clay, Hard

# %%
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
players_df

# %% [markdown]
# - We keep only the players that have played at least 15 games in total and at least 3 games in each surface for better correlation results. 

# %%
players_df = players_df.loc[(players_df["Total_Games"]>15) & (players_df["Total_Grass_Games"]>3) & (players_df["Total_Hard_Games"]>3) & (players_df["Total_Clay_Games"]>3)]

# %%
players_df.isnull().sum()



# %% [markdown]
# # Implementation of an improved Elo model 

# %% [markdown]
# Given the above information we conclude that tennis players performance varies across surfaces. Their performance in Grass and Hard surfaces is highly correlated whereas in Grass and Clay is not. To incorporate that in our Elo model we will implement an adjusted Elo model that considers the surface that the game is played. For that we will calculate each player's Elo rating in the three main surfaces alongside their standard Elo and combine them to derive a more accurate prediction.

# %% [markdown]
# - We make the simplest adjustment to weight each type of Elo equally. So we take the midpoint of the standard Elo and the surface specific Elo. This implementation may not be optimal and further exploration is needed so the optimal weights regarding model prediction parfomance can be derived.

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
        if  surface == "grass":           
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
            ranking_elo.append((adj_elo[data.iloc[i,:].Winner],adj_elo[data.iloc[i,:].Loser],data.iloc[i,:].Winner,data.iloc[i,:].Loser,data.iloc[i,:].Odds,data.iloc[i,:].Date))
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
            ranking_elo.append((adj_elo[data.iloc[i,:].Winner],adj_elo[data.iloc[i,:].Loser],data.iloc[i,:].Winner,data.iloc[i,:].Loser,data.iloc[i,:].Odds,data.iloc[i,:].Date))    
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
            ranking_elo.append((adj_elo[data.iloc[i,:].Winner],adj_elo[data.iloc[i,:].Loser],data.iloc[i,:].Winner,data.iloc[i,:].Loser,data.iloc[i,:].Odds,data.iloc[i,:].Date))
        #Carpet    
        else:       
            adj_elo[w]=new_elow
            adj_elo[l]=new_elol
            ranking_elo.append((adj_elo[data.iloc[i,:].Winner], adj_elo[data.iloc[i,:].Loser],data.iloc[i,:].Winner,data.iloc[i,:].Loser,data.iloc[i,:].Odds,data.iloc[i,:].Date))
    ranking_elo=pd.DataFrame(ranking_elo,columns=["Adj_Elo_Winner","Adj_Elo_Loser","Winner","Loser","Odds","Date"])  
   # ranking_elo["Prob_Adj_Elo"]=1 / (1 + 10 ** ((ranking_elo["Adj_Elo_Loser"] - ranking_elo["Adj_Elo_Winner"]) / 400))
    #ranking_elo["Prob_Adj_Elo_Fav"]=ranking_elo.apply(lambda x: 1 / (1 + 10 ** ((x["Adj_Elo_Loser"] - x["Adj_Elo_Winner"]) / 400)) if x["Adj_Elo_Loser"] < x["Adj_Elo_Winner"] else 1 / (1 + 10 ** ((x["Adj_Elo_Winner"] - x["Adj_Elo_Loser"]) / 400)),axis=1)
    ranking_elo["Prob_Adj_Elo1"]=1 / (1 + 10 ** ((ranking_elo["Adj_Elo_Loser"] - ranking_elo["Adj_Elo_Winner"]) / 400))   
    ranking_elo["Prob_Adj_Elo"]=ranking_elo.apply(lambda x: 1-x['Prob_Adj_Elo1'] if x['Prob_Adj_Elo1']<0.5 else x['Prob_Adj_Elo1'],axis=1 )    
    
    
    ranking_elo["Elo_Winner"]=ranking_elo.apply(lambda x: 'EloFav' if x['Prob_Adj_Elo1'] >0.5 else 'EloDog',axis=1)
    ranking_elo["Elo_Fav"]=ranking_elo.apply(lambda x: x['Winner'] if x['Adj_Elo_Winner'] > x['Adj_Elo_Loser'] else x['Loser'],axis=1)
    
    return ranking_elo

pd.set_option('display.float_format', lambda x: '%.6f' % x)    #convert to float format to avoid scientific notation

adj_elo_rankings = get_adj_elo_rankings(data)
adj_elo_rankings=adj_elo_rankings[adj_elo_rankings["Adj_Elo_Winner"]!=1500]
adj_elo_rankings=adj_elo_rankings[adj_elo_rankings["Adj_Elo_Loser"]!=1500]
adj_elo_rankings=adj_elo_rankings[adj_elo_rankings["Prob_Adj_Elo"].lt(0.4)|adj_elo_rankings["Prob_Adj_Elo"].gt(0.6)]
#|adj_elo_rankings["Adj_Elo_Loser"]!='1500']
(adj_elo_rankings[["Adj_Elo_Winner", "Adj_Elo_Loser", "Prob_Adj_Elo1","Prob_Adj_Elo","Elo_Winner","Elo_Fav","Winner","Loser","Odds","Date"]]).to_sql("Elo",con=devengine,index=False,if_exists='replace')


