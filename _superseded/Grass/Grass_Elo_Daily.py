import datetime
from sqlite3 import connect
from matplotlib.pyplot import contour
import requests
from bs4 import BeautifulSoup
import argparse
import datetime
from tabulate import tabulate
import pandas as pd
from Tennis import *
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

username = r"ChrisDB"
password = "babinda08"
server = r"localhost"
database = "Bets"
devconnection_uri = "mssql+pymssql://{}:{}@{}/{}".format(
    username, password, server, database)
devengine = create_engine(devconnection_uri)

connection = devengine.connect()


def Main(url, current_date, suffix, check):

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0)

    args = parser.parse_args()
    response = requests.get(url)

    # # Analysis with beautifulsoup
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find("table", {"class": "result"})
    table = soup.findAll("table", {"class": "result"})[1]
    if(check == 1):
        table = soup.find("table", {"class": "result"})
    table_body = table.find('tbody')

    rows = table_body.find_all('tr')
    tournament_idx_lst = []
    for i, row in enumerate(rows):
        if '<tr class="head flags">' in str(row):
            t_name = row.find("td", {"class": "t-name"}).text
            tournament_idx_lst.append(i)

    tournament_idx_lst.append(len(rows))

    def getPlayersFullName(playerUrl):
        player_url = 'https://www.tennisexplorer.com' + playerUrl
        player_response = requests.get(player_url)
        player_soup = BeautifulSoup(player_response.content, 'html.parser')
        player_table = player_soup.find("table", {"class": "plDetail"})
        player_table_body = player_table.find('tbody')
        try:
            player_rank = player_table_body.text.split(
                'Current/Highest rank - singles: ')[1].split(".")[0]
            if '-' in player_rank:
                player_rank = "10000"
        except:
            player_rank = "10000"
        try:
            player_hand = player_table_body.text.split(
                'Plays: ')[1].split(".")[0]
        except:
            player_hand = 'right'
        player_name = player_table_body.find_all('h3')
        name = ' '.join(player_name[0].text.split())
        splitname = name.split(' ')
        first_name = splitname[-1]
        last_name = name.replace(' '+first_name, '')
        name = first_name + ' ' + last_name
        name = name.replace('Carlos Alcaraz Garfia','Carlos Alcaraz').replace(
            'Lesya Tsurenko', 'Lesia Tsurenko').replace(
            'Harry Fritz Taylor', 'Taylor Fritz').replace(
                'Manuel Cerundolo Juan', "Juan Manuel Cerundolo").replace(
                    'Martin Etcheverry Tomas', 'Tomas Martin Etcheverry').replace(
                    'John Wolf Jeffrey', 'Jeffrey John Wolf').replace(
            'Victor Cornea Vlad', 'Vlad Victor Cornea').replace(
            'Cristian Jianu Filip', 'Filip Cristian Jianu').replace(
                'Pablo Ficovich Juan', 'Juan Pablo Ficovich').replace(
                    'Felipe Meligeni Rodrigues Alves', 'Felipe Meligeni Alves').replace(
                        'Hsin Tseng Chun', 'Chun Hsin Tseng').replace(
                    'Woo Kwon Soon', 'Soon Woo Kwon').replace(
                        'Moura Monteiro Thiago', 'Thiago Monteiro').replace(
                            'Viktoria Azarenka', 'Victoria Azarenka').replace(
                                'McHugh', 'Mchugh').replace(
                                    'Fco. Vidal Azorin Jose', 'Jose Fco Vidal Azorin').replace(
                                        'Bautista Torres Juan', 'Juan Bautista Torres').replace(
                                'Marco Moroni Gian', 'Gian Marco Moroni').replace(
                                    'Danielle Collins', 'Danielle Rose Collins').replace(
                                        'Pablo Varillas Juan', 'Juan Pablo Varillas').replace(
                                            'Sorana-Mihaela Cirstea', 'Sorana Cirstea').replace(
                                                'Mackenzie McDonald', 'Mackenzie Mcdonald').replace(
            'Irina Begu', 'Irina Camelia Begu').replace(
            'Adina Cristian Jaqueline', 'Jaqueline Adina Cristian').replace(
                'A. Stephens Sloane', 'Sloane Stephens').replace(
                    'Kenny de Schepper', 'Kenny De Schepper').replace(
                    'Matthieu Perchicot', 'Mathieu Perchicot').replace(
                        'Camila Osorio Serrano Maria', 'Camila Osorio').replace(
                            'Maria Bara Irina', 'Irina Maria Bara').replace(
                                'Milan Zekic', 'Miljan Zekic').replace(
                                    'Anna Schmiedlova Karolina', 'Anna Karolina Schmiedlova').replace(
                                        'Annie Fernandez Leylah', 'Leylah Annie Fernandez').replace(
                                            'Xinyu Wang', 'Xin Yu Wang').replace(
                                                'Ignacio Londero Juan','Juan Ignacio Londero'
                                            )
        return name.strip().replace('-', ' ') + '(' + player_rank + ')'

    tournament_dict = {
    }
    for i, item in enumerate(tournament_idx_lst[:-1]):

        tournament_name = rows[item].find("td", class_="t-name").text.strip()
        if 'Futures' not in tournament_name and 'ITF' not in tournament_name:            
            tournament_url = rows[item].find(
                "td", class_="t-name").contents[0].attrs['href']
            tournament_url = 'https://www.tennisexplorer.com' + \
                tournament_url.replace("'", '')
            response = requests.get(tournament_url)

            # # Analysis with beautifulsoup
            soup = BeautifulSoup(response.content, 'html.parser')
            court_type = soup.find("div", {"id": "center"}).text.split('\n')[
                2].split(")")[0].split(",")[-2].strip()
            court_type = court_type.replace(
                "indoors", "Hard").replace('clay', 'Clay').replace('hard', 'Hard')
            if court_type != 'grass':
                continue
            if not 'Futures' in tournament_name:
                if not tournament_dict.get(tournament_name):
                    tournament_dict[tournament_name+str(item)] = {}
                    tournament_dict[tournament_name+str(item)][current_date] = []
                for c in range(item+1, tournament_idx_lst[i+1], 2):
                    test=rows[c].findAll(
                        "td", class_="course")
                    #print(len(test))
                    if len(test)>1:
                        tournament_dict[tournament_name+str(item)][current_date].append(getPlayersFullName(rows[c].find(
                            "td", class_="t-name").a['href']) + ' vs ' + getPlayersFullName(rows[c+1].find("td", class_="t-name").a['href']) + ":" + court_type + ":" + rows[c].findAll(
                            "td", class_="course")[0].contents[0] + "_" + rows[c].findAll(
                            "td", class_="course")[1].contents[0])
                    else:
                        tournament_dict[tournament_name+str(item)][current_date].append(getPlayersFullName(rows[c].find(
                            "td", class_="t-name").a['href']) + ' vs ' + getPlayersFullName(rows[c+1].find("td", class_="t-name").a['href']) + ":" + court_type + ":" + rows[c].findAll(
                            "td", class_="coursew")[0].contents[0] + "_" + rows[c].findAll(
                            "td", class_="course")[0].contents[0])                        

    df = pd.DataFrame(columns=['Sex', 'Tournament', 'Player 1', 'Player 1 Elo', 'Player 2', 'Player 2 Elo','Elo Favourite','Elo Difference','Elo Probability','Estimated Odds','Actual Odds','Estimated Odds Clay'])
    for key, value in tournament_dict.items():
        # print(value)
        datefilename = current_date.replace("-", "")

        #with xlsxwriter.Workbook(r"C:\Users\chris\OneDrive\Desktop\Tennis\\" + key + datefilename + suffix + ".xlsx") as workbook:
        for i, date in value.items():
            for match in date:
                match1 = match.split(':')[0]
                players = match1.split(' vs ')
                player1 = players[0].split('(')[0]
                player2 = players[1].split('(')[0]
                odds=match.split(':')[2]
                player1odds=odds.split("_")[0]
                player2odds=odds.split("_")[1]
                Surface = match.split(':')[1]
                #print(Surface)
                #print(player1odds,player2odds)
                

                if ValidName(player2) == True and ValidName(player1)==True:
                    Elo_player1, Elo_player2,Fav,elo_diff,Prob,Odds,ActualOdds,OddsClay,OddsHard,EloDiffClay,EloDiffHard,RankDiff=GetElo(player1,player2,player1odds,player2odds)

                    #Prob="{:.2%}".format(Prob)
                    Odds="{:.2}".format(Odds)
                    OddsClay="{:.2}".format(OddsClay)
                    OddsHard="{:.2}".format(OddsHard)
                    table = [['Date','Sex', 'Tournament', 'Player 1', 'Player 1 Elo', 'Player 2',\
                         'Player 2 Elo','Elo Favourite','Elo Difference','Elo Probability','Estimated Odds',\
                             'Actual Odds', 'Estimated Odds grass','Estimated Odds Hard','Surface','Elo Difference grass','Elo Difference Hard','RankDiff'], [datefilename,
                            suffix.replace('_', ''), key, player1, Elo_player1, player2, Elo_player2,Fav,elo_diff,Prob,Odds,ActualOdds,OddsClay,OddsHard,Surface,EloDiffClay,EloDiffHard,RankDiff]]
                        
                    df=pd.DataFrame(table)
                    headers = df.iloc[0]
                    new_df = pd.DataFrame(df.values[1:], columns=headers)
                    new_df["RankDiff"]=new_df["RankDiff"].astype(str)
                    #filter=new_df['Elo Probability'].gt(0.5)|new_df['Estimated Odds Clay'].gt(0.5)|new_df['Estimated Odds Hard'].gt(0.5)
                    #new_df=new_df[filter]
                    new_df.to_sql("Test_daily_grass",con=devengine,if_exists='append',index=False)

#for x in range(81,90):
for x in range(0,1):
    
    connection.execute('Delete FROM Test_Daily_grass')
    connection.execute('Delete FROM bets_today_grass')
    # # Get the current date
    tomorrow = datetime.datetime.now() + datetime.timedelta(days=-x)
    print(tomorrow)
    year, month, day = tomorrow.year, tomorrow.month, tomorrow.day
    current_date = str(year) + '-' + str(month) + '-' + str(day)
    #print('https://www.tennisexplorer.com/matches/?type=atp-single&year={}&month={}&day={}'.format(year, month, day))

    Main('https://www.tennisexplorer.com/matches/?type=atp-single&year={}&month={}&day={}'.format(year,
        month, day), current_date, "_Mens", 1)
    Main('https://www.tennisexplorer.com/matches/?type=wta-single&year={}&month={}&day={}'.format(year,
        month, day), current_date, "_Womens", 1)

    Main('https://www.tennisexplorer.com/matches/?type=atp-single&year={}&month={}&day={}'.format(year,
        month, day), current_date, "_Mens", 0)
    Main('https://www.tennisexplorer.com/matches/?type=wta-single&year={}&month={}&day={}'.format(year,
        month, day), current_date, "_Womens", 0)
    
    Filterdf=pd.read_sql_query("Select * From Test_daily_grass",con=devengine)
    bra=Filterdf[(Filterdf['Elo Probability'] != '<65%')]
    bra1=bra[(bra['Player 1 Elo'] != "0")]
    bra2=bra1[(bra1['Player 2 Elo'] != "0")]
    bra3=bra2[(bra2['Elo Probability'] != '>65%')]
    bra3=bra3.drop(columns=["Player 1 Elo", "Player 2 Elo"])
    #bra3["Estimated Odds"]=bra3["Estimated Odds"].astype(float)
    #bra3["Actual Odds"]=bra3["Actual Odds"].astype(float)
    bra3["Estimated Odds grass"]=bra3["Estimated Odds grass"].astype(float)
    bra3["Estimated Odds Hard"]=bra3["Estimated Odds Hard"].astype(float)
    bra3["Estimated Odds"]=bra3["Estimated Odds"].astype(float)
    #bra3["Actual Odds"]=bra3["Actual Odds"].astype(float)
    bra3['Actual Odds']=bra3['Actual Odds'].apply(lambda x: str(x).replace(u'\xa0', u''))
    filter=(bra3['Estimated Odds'].lt(2)|bra3['Estimated Odds grass'].lt(2)|bra3['Estimated Odds Hard'].lt(2))
    bra3=bra3[filter]
    bra4=bra3[bra3['Actual Odds']!='']
    filter2=(bra4['Estimated Odds'].gt(1)|bra4['Estimated Odds grass'].gt(1))
    bra4=bra4[filter2]

    #bra3["Odds Difference"]=(bra3["Actual Odds"] - bra3["Estimated Odds"]).map('${:,.2f}'.format)
    #bra3["Odds Difference Clay"]=(bra3["Actual Odds"] - bra3["Estimated Odds Clay"]).map('${:,.2f}'.format)
    bra4.to_sql("bets_today_grass",con=devengine,index=False,if_exists="append")