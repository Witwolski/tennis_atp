# %%
from dataclasses import replace
import pandas as pd
import numpy as np
import os
import datetime
import matplotlib.pyplot as plt
from sqlalchemy import create_engine
import sys

username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database)
devengine = create_engine(devconnection_uri)

def elo_prev():
    df = pd.read_sql_query("Select tournament, [player 1],[player 2], [elo favourite],[estimated odds],[actual odds],[surface] FROM bets_yesterday where date like '20225%'  \
     and [estimated odds] <[actual odds] ",con=devengine)

    df=df[df['estimated odds']!=1]
    def OddsRange(df,thresh_high,thresh_low):
        mask=(df['actual odds'] > thresh_low) & (df['actual odds'] < thresh_high) & (df['estimated odds'] < df['actual odds'])
        df=df[mask]
        #df.to_excel(str(thresh_high)+'.xlsx',index=False)
        return df

    def RangeWinPercentage(df,thresh_high):
        count=0
        for _,row in df.iterrows():
            if row['player 1']==row['elo favourite']:
                count=count+1
        if len(df.index) > 9:  
            Stake=1000
            df["Profit"]=df.apply(lambda x: -Stake if x["player 1"]!=x["elo favourite"] else (x["actual odds"]*Stake)-Stake,axis=1)
            df.loc['Profit']= df.sum(axis=0)   
            print(thresh_high)               
            print(len(df.index) , 'Matches')
            print(count/len(df.index))
            print(df["Profit"].iloc[-1])
        

    for y in range(1,4):
        for x in range(-1,10):
            thresh_high=y+(x*0.1)+0.1
            thresh_low=y+(x*0.1)
            filtered_df=OddsRange(df,thresh_high,thresh_low)
            #print(thresh_low,thresh_high)
            RangeWinPercentage(filtered_df,thresh_high)
            print()

def elo_Mbm():
    df = pd.read_sql_query("Select * FROM elo_mbm  where date like '%2022%' --and surface  like 'grass'",con=devengine)
    df.iloc[0]


    def OddsRange(df,thresh_high,thresh_low):
        mask=(df['Elo_Fav_Odds'] > thresh_low) & (df['Elo_Fav_Odds'] < thresh_high) & (df['Elo_Est_Odds'] < df['Elo_Fav_Odds'] )
        df=df[mask]
        return df

    def RangeWinPercentage(df,thresh_high):
        count=0
        for _,row in df.iterrows():
            if row['Winner']==row['Elo_Fav']:
                count=count+1
        if len(df.index) > 9:      
            percentage=(count/len(df.index))
            if (percentage)>0.4:
                Stake=100
                df["Profit"]=df.apply(lambda x: -Stake if x["Winner"]!=x["Elo_Fav"] else (x["Elo_Fav_Odds"]*Stake)-Stake,axis=1)
                df.loc['Profit']= df.sum(axis=0)
                if df["Profit"].iloc[-1] > 1:
                    #df.to_excel('test.xlsx')
                    #print(df.iloc[-1])
                    print(thresh_high)
                    #print(len(df.index) , 'Matches')
                    #print(percentage)
                    print(df["Profit"].iloc[-1])
                    print()
                df.to_excel(str(thresh_high)+'.xlsx',index=False)

    for y in range(1,3):
        for x in range(-1,10):
            thresh_high=y+(x*0.1)+0.1
            thresh_low=y+(x*0.1)
            #thresh_high=2.2
            #thresh_low=1.8        
            filtered_df=OddsRange(df,thresh_high,thresh_low)
            #print(thresh_low,thresh_high)
            RangeWinPercentage(filtered_df,thresh_high)
        '''    
        for z in range(-1,10):
            thresh_high=y+(z*0.1)+0.1
            thresh_low=y+(z*0.1)-0.05
            #thresh_high=2.2
            #thresh_low=1.8        
            filtered_df=OddsRange(df,thresh_high,thresh_low)
            #print(thresh_low,thresh_high)
            RangeWinPercentage(filtered_df,thresh_high)        
        '''    

def elo_Mbm_Adj():
    df = pd.read_sql_query("Select * FROM elo_mbm_adj  where date like '%2022%' --and surface  like 'grass'",con=devengine)
    df.iloc[0]


    def OddsRange(df,thresh_high,thresh_low):
        mask=(df['Elo_Fav_Odds'] > thresh_low) & (df['Elo_Fav_Odds'] < thresh_high) & (df['Elo_Fav_Est_Odds'] >= df['Elo_Fav_Odds'] )
        df=df[mask]
        return df

    def RangeWinPercentage(df,thresh_high):
        count=0
        for _,row in df.iterrows():
            if row['Winner']==row['Elo_Fav']:
                count=count+1
        if len(df.index) > 9:      
            percentage=(count/len(df.index))
            if (percentage)>0.4:
                Stake=100
                df["Profit"]=df.apply(lambda x: -Stake if x["Winner"]!=x["Elo_Fav"] else (x["Elo_Fav_Odds"]*Stake)-Stake,axis=1)
                df.loc['Profit']= df.sum(axis=0)
                if df["Profit"].iloc[-1] > 1:
                    #df.to_excel('test.xlsx')
                    #print(df.iloc[-1])
                    print(thresh_high)
                    #print(len(df.index) , 'Matches')
                    #print(percentage)
                    print(df["Profit"].iloc[-1])
                    print()
                #df.to_excel(str(thresh_high)+'.xlsx',index=False)

    for y in range(1,3):
        for x in range(-1,10):
            thresh_high=y+(x*0.1)+0.1
            thresh_low=y+(x*0.1)
            #thresh_high=2.2
            #thresh_low=1.8        
            filtered_df=OddsRange(df,thresh_high,thresh_low)
            #print(thresh_low,thresh_high)
            RangeWinPercentage(filtered_df,thresh_high)
        '''    
        for z in range(-1,10):
            thresh_high=y+(z*0.1)+0.1
            thresh_low=y+(z*0.1)-0.05
            #thresh_high=2.2
            #thresh_low=1.8        
            filtered_df=OddsRange(df,thresh_high,thresh_low)
            #print(thresh_low,thresh_high)
            RangeWinPercentage(filtered_df,thresh_high)        
        '''    

def elo_Mbm_Adj_Dog():
    df = pd.read_sql_query("Select * FROM elo_mbm_adj  where date like '%2022%' --and surface  like 'grass'",con=devengine)
    df.iloc[0]


    def OddsRange(df,thresh_high,thresh_low):
        mask=(df['Elo_Dog_Odds'] > thresh_low) & (df['Elo_Dog_Odds'] < thresh_high) & (df['Elo_Dog_Est_Odds'] >= df['Elo_Dog_Odds'] )
        df=df[mask]
        return df

    def RangeWinPercentage(df,thresh_high):
        count=0
        for _,row in df.iterrows():
            if row['Winner']!=row['Elo_Fav']:
                count=count+1
        if len(df.index) > 9:      
            percentage=(count/len(df.index))
            if (percentage)>0.4:
                Stake=100
                df["Profit"]=df.apply(lambda x: -Stake if x["Winner"]==x["Elo_Fav"] else (x["Elo_Dog_Odds"]*Stake)-Stake,axis=1)
                df.loc['Profit']= df.sum(axis=0)
                if df["Profit"].iloc[-1] > 1:
                    #df.to_excel('test.xlsx')
                    #print(df.iloc[-1])
                    print(thresh_high)
                    #print(len(df.index) , 'Matches')
                    #print(percentage)
                    print(df["Profit"].iloc[-1])
                    print()
                #df.to_excel(str(thresh_high)+'.xlsx',index=False)

    for y in range(1,3):
        for x in range(-1,10):
            thresh_high=y+(x*0.1)+0.1
            thresh_low=y+(x*0.1)
            #thresh_high=2.2
            #thresh_low=1.8        
            filtered_df=OddsRange(df,thresh_high,thresh_low)
            #print(thresh_low,thresh_high)
            RangeWinPercentage(filtered_df,thresh_high)
        '''    
        for z in range(-1,10):
            thresh_high=y+(z*0.1)+0.1
            thresh_low=y+(z*0.1)-0.05
            #thresh_high=2.2
            #thresh_low=1.8        
            filtered_df=OddsRange(df,thresh_high,thresh_low)
            #print(thresh_low,thresh_high)
            RangeWinPercentage(filtered_df,thresh_high)        
        '''    



sys.stdout = open('Higher.txt', 'w')
#print('MBM')
#elo_Mbm()
print('#############################')
print('MBM_Adj')
#elo_Mbm_Adj_Dog()
elo_Mbm_Adj()
#elo_prev()
sys.stdout.close()
