import csv
import pprint
import datetime
import glob
import sys
import operator
import itertools
import collections
from operator import itemgetter
from collections import OrderedDict
import json
from typing import Set
import numpy as np
import pandas as pd
import math
from pandas import Categorical
from itertools import islice


def analyzeSets(row, name):
    #name = 'Leylah Annie Fernandez'
    """helper function"""
    sets = row['score'].split(' ')
    won = 0
    lost = 0
    first = 0
    res = 0
    second = 0
    firstlost = 0
    secondlost = 0
    rankedhigher = 0
    firstvhigherrank = 0
    firstvlowerrank = 0
    secondvhigherrank = 0
    secondvlowerrank = 0
    firstlostvhigherrank = 0
    firstlostvlowerrank = 0
    secondlostvhigherrank = 0
    secondlostvlowerrank = 0

    for idx, set in enumerate(sets):
        setscore = set.split('-')
        setscore[0] = setscore[0].replace('[', '')
        setscore[1] = setscore[1].replace(']', '')
        if (len(setscore) > 1):
            # clean tb scores
            if('(' in setscore[0]):
                setscore[0] = setscore[0][0]
            if('(' in setscore[1]):
                setscore[1] = setscore[1][0]
            if(row['winner_name'] == name):
                if row['winner_rank'] > row['loser_rank']:
                    rankedhigher = 0
                else:
                    rankedhigher = 1
               # print('player winner')
                if((int(setscore[0]) > int(setscore[1])) & (int(setscore[0]) > 5)):
                    won = won+1
                    if(idx == 0):
                        first = 1
                        if rankedhigher == 1:
                            firstvlowerrank = 1
                        else:
                            firstvhigherrank = 1
                    elif(idx == 1):
                        second = 1
                        if rankedhigher == 1:
                            secondvlowerrank = 1
                        else:
                            secondvhigherrank = 1
                elif(int(setscore[0]) < int(setscore[1])):
                    lost = lost+1
                    if(idx == 0):
                        firstlost = 1
                        if rankedhigher == 1:
                            firstlostvlowerrank = 1
                        else:
                            firstlostvhigherrank = 1
                    elif(idx == 1):
                        secondlost = 1
                        if rankedhigher == 1:
                            secondlostvlowerrank = 1
                        else:
                            secondlostvhigherrank = 1
            else:
                if row['winner_rank'] > row['loser_rank']:
                    rankedlower = 1
                else:
                    rankedlower = 0
                if((int(setscore[0]) < int(setscore[1])) & (int(setscore[1]) > 5)):
                    won = won+1
                    if(idx == 0):
                        first = 1
                        if rankedlower == 1:
                            firstvlowerrank = 1
                        else:
                            firstvhigherrank = 1
                    elif(idx == 1):
                        second = 1
                        if rankedlower == 1:
                            secondvlowerrank = 1
                        else:
                            secondvhigherrank = 1
                elif((int(setscore[0]) > int(setscore[1]))):
                    lost = lost+1
                    if(idx == 0):
                        firstlost = 1
                        if rankedlower == 1:
                            firstlostvlowerrank = 1
                        else:
                            firstlostvhigherrank = 1
                    elif(idx == 1):
                        secondlost = 1
                        if rankedlower == 1:
                            secondlostvlowerrank = 1
                        else:
                            secondlostvhigherrank = 1
        # print(setscore)
    return(str(won)+','+str(lost)+','+str(first)+','+str(res) + ',' + str(second) + ',' + str(firstlost) + ',' + str(secondlost)
           + ',' + str(firstvhigherrank) + ',' + str(firstvlowerrank)
           + ',' + str(secondvhigherrank) + ',' + str(secondvlowerrank)
           + ',' + str(firstlostvhigherrank) + ',' + str(firstlostvlowerrank)
           + ',' + str(secondlostvhigherrank) + ',' + str(secondlostvlowerrank))

def readChall_QATPMatches(dirname):
    """reads Challenger level + ATP Q matches but does not parse time into datetime objects"""
    allFiles = glob.glob(dirname + "/atp_matches_qual_chall_" + "2021.csv") + glob.glob(dirname + "/atp_matches_qual_chall_" + "2022.csv")
    matches = pd.DataFrame()
    container = list()
    for filen in allFiles:
        df = pd.read_csv(filen,
                         index_col=None,
                         header=0)
        container.append(df)
    matches = pd.concat(container)
    return matches

def readITFMatches(dirname):
    """reads Challenger level + ATP Q matches but does not parse time into datetime objects"""
    allFiles = glob.glob(dirname + "/atp_matches_futures_" + "2021.csv") +glob.glob(dirname + "/atp_matches_futures_" + "2022.csv")
    matches = pd.DataFrame()
    container = list()
    for filen in allFiles:
        df = pd.read_csv(filen,
                         index_col=None,
                         header=0)
        container.append(df)
    matches = pd.concat(container)
    return matches

def readATPMatches(dirname):
    """Reads ATP matches but does not parse time into datetime object"""
    allFiles = glob.glob(dirname + "/atp_matches_" + "2021.csv")+glob.glob(dirname + "/atp_matches_" + "2022.csv")
    matches = pd.DataFrame()
    container = list()
    for filen in allFiles:
        df = pd.read_csv(filen,
                         index_col=None,
                         header=0)
        container.append(df)
    matches = pd.concat(container)
    return matches

def readWTAMatches(dirname):
    """Reads ATP matches but does not parse time into datetime object"""
    allFiles = glob.glob(dirname + "/wta_matches_" + "2021.csv") + glob.glob(dirname + "/wta_matches_" + "2022.csv")
    matches = pd.DataFrame()
    container = list()
    for filen in allFiles:
        df = pd.read_csv(filen,
                         index_col=None,
                         header=0)
        container.append(df)
    matches = pd.concat(container)
    return matches

def geth2hforplayer(allmatches, name):
    """get all head-to-heads of the player"""
    matches = allmatches
    matches = matches[(matches['winner_name'] == name) |
                      (matches['loser_name'] == name)]
    h2hs = {}
    for index, match in matches.iterrows():
        if (match['winner_name'] == name):
            # if (match['loser_name'] not in h2hs):
            h2hs[index] = {}
            #h2hs[match['loser_name']]['l'] = 0
            h2hs[index]['Rank'] = match['winner_rank']
            h2hs[index]['OppositionRank'] = match['loser_rank']
            h2hs[index]['w'] = 'Win'
            h2hs[index]['Score'] = match['score']
            h2hs[index]['Surface'] = match['surface']
            h2hs[index]['Opposition'] = match['loser_name']
            # else:
            #    h2hs[match['loser_name']]['w'] = h2hs[match['loser_name']]['w']+1
        elif (match['loser_name'] == name):
            # if (match['winner_name'] not in h2hs):
            h2hs[index] = {}
            h2hs[index]['w'] = 'Loss'
            h2hs[index]['Rank'] = match['loser_rank']
            h2hs[index]['OppositionRank'] = match['winner_rank']
            #h2hs[match['winner_name']]['l'] = 1
            h2hs[index]['Score'] = match['score']
            h2hs[index]['Surface'] = match['surface']
            h2hs[index]['Opposition'] = match['winner_name']
            # else:
            #    h2hs[match['winner_name']]['l'] = h2hs[match['winner_name']]['l']+1

    # create list
    h2hlist = []
    for k, v in h2hs.items():
        h2hlist.append([k, v['Opposition'], v['Surface'], v['w'],
                       v['Score'], v['Rank'], v['OppositionRank']])
    # sort by wins and then by losses + print
    # filter by h2hs with more than 6 wins:
    #h2hlist = [i for i in h2hlist if i[1] > 6]
    if (len(h2hlist) == 0):
        return ''
    else:
        return h2hlist
        #sorted(h2hlist, key=itemgetter(1,2))
        # for h2h in h2hlist:
        #    print(name+';'+h2h[0]+';'+str(h2h[1])+';'+str(h2h[2]))

def setstats(allmatches, Surface, name,opprank):
    SetTable = []
    """for a player calculates specific set statistics"""
    atpmatches = allmatches
    matches = atpmatches[(atpmatches['winner_name'] == name)
                         | (atpmatches['loser_name'] == name)]

    matches = matches[matches['surface'] == Surface]
    # setfilter
    # matches = matches[(matches['score'].str.count('-') == 3)
    #                  | (matches['score'].str.count('-') == 2)]
    # norets
    matches = matches[~matches['score'].str.contains('RET|W').fillna(False)]
    # sets=matches.apply(analyzeSets,args=(name,),axis=1)
    matches['sets_analysis'] = matches.apply(analyzeSets, args=(name,), axis=1)
    matches['sets_won'], matches['sets_lost'], matches['first'], matches['res'], matches['second'], matches['firstlost'], matches['secondlost'], matches['firstvhigherrank'], matches['firstvlowerrank'], matches['secondvhigherrank'], matches['secondvlowerrank'], matches['firstlostvhigherrank'], matches['firstlostvlowerrank'], matches['secondlostvhigherrank'], matches['secondlostvlowerrank'] = zip(
        *matches['sets_analysis'].map(lambda x: x.split(',')))
       
    
    matches['sets_won'] = matches['sets_won'].astype('int')
    matches['sets_lost'] = matches['sets_lost'].astype('int')
    matches['first'] = matches['first'].astype('int')
    matches['second'] = matches['second'].astype('int')
    matches['firstlost'] = matches['firstlost'].astype('int')
    matches['secondlost'] = matches['secondlost'].astype('int')
    matches['firstvhigherrank'] = matches['firstvhigherrank'].astype('int')
    matches['firstvlowerrank'] = matches['firstvlowerrank'].astype('int')
    matches['secondvhigherrank'] = matches['secondvhigherrank'].astype('int')
    matches['secondvlowerrank'] = matches['secondvlowerrank'].astype('int')
    matches['firstlostvhigherrank'] = matches['firstlostvhigherrank'].astype(
        'int')
    matches['firstlostvlowerrank'] = matches['firstlostvlowerrank'].astype(
        'int')
    matches['secondlostvhigherrank'] = matches['secondlostvhigherrank'].astype(
        'int')
    matches['secondlostvlowerrank'] = matches['secondlostvlowerrank'].astype(
        'int')

    firstsettotal = matches['first'].sum() + matches['firstlost'].sum()
    firstsettotalpercent = matches['first'].sum()/firstsettotal
    secondsettotal = matches['second'].sum() + matches['secondlost'].sum()
    secondsettotalpercent = matches['second'].sum()/secondsettotal
    #print('first sets won: ' + str(matches['first'].sum()) + '\\' + str(
    #    firstsettotal) + ' (' + "{:.0%}".format(firstsettotalpercent) + ')')
    SetTable.append('first sets won: ' + str(matches['first'].sum()) + '\\' + str(
        firstsettotal) + ' (' + "{:.0%}".format(firstsettotalpercent) + ')')    
    firstsethightotal = matches['firstvhigherrank'].sum(
    ) + matches['firstlostvhigherrank'].sum()
    try:
        if firstsethightotal > 0:
            firstsethightotalpercent = matches['firstvhigherrank'].sum(
            )/firstsethightotal
        else:
            firstsethightotalpercent = 0
        if opprank == 'Higher':
            #print('first sets v higher rank: ' + str(matches['firstvhigherrank'].sum()) + '\\' + str(
            #    firstsethightotal) + ' (' + "{:.0%}".format(firstsethightotalpercent) + ')')
            SetTable.append('first sets v higher rank: ' + str(matches['firstvhigherrank'].sum()) + '\\' + str(
                firstsethightotal) + ' (' + "{:.0%}".format(firstsethightotalpercent) + ')')    
        else:
            firstsetlowtotal = matches['firstvlowerrank'].sum(
            ) + matches['firstlostvlowerrank'].sum()

            firstsetlowtotalpercent = matches['firstvlowerrank'].sum()/firstsetlowtotal
            #print('first sets v lower rank: ' + str(matches['firstvlowerrank'].sum()) + '\\' + str(
            #    firstsetlowtotal) + ' (' + "{:.0%}".format(firstsetlowtotalpercent) + ')')
            SetTable.append('first sets v lower rank: ' + str(matches['firstvlowerrank'].sum()) + '\\' + str(
                firstsetlowtotal) + ' (' + "{:.0%}".format(firstsetlowtotalpercent) + ')')

    except Exception:
        SetTable.append('')

    #print('second sets won: ' + str(matches['second'].sum()) + '\\' + str(
    #    secondsettotal) + ' (' + "{:.0%}".format(secondsettotalpercent) + ')')
    SetTable.append('second sets won: ' + str(matches['second'].sum()) + '\\' + str(
        secondsettotal) + ' (' + "{:.0%}".format(secondsettotalpercent) + ')')

    secondsethightotal = matches['secondvhigherrank'].sum(
    ) + matches['secondlostvhigherrank'].sum()
    if secondsethightotal >0:
        secondsethightotalpercent = matches['secondvhigherrank'].sum(
        )/secondsethightotal
    else:
        secondsethightotalpercent =0
    if opprank == 'Higher':
        #print('second sets v higher rank: ' + str(matches['secondvhigherrank'].sum()) + '\\' + str(
        #    secondsethightotal) + ' (' + "{:.0%}".format(secondsethightotalpercent) + ')')
        SetTable.append('second sets v higher rank: ' + str(matches['secondvhigherrank'].sum()) + '\\' + str(
            secondsethightotal) + ' (' + "{:.0%}".format(secondsethightotalpercent) + ')')
    else:
        secondsetlowtotal = matches['secondvlowerrank'].sum(
        ) + matches['secondlostvlowerrank'].sum()
        try:
            secondsetlowtotalpercent = matches['secondvlowerrank'].sum(
            )/secondsetlowtotal
            #print('second sets v lower rank: ' + str(matches['secondvlowerrank'].sum()) + '\\' + str(
            #    secondsetlowtotal) + ' (' + "{:.0%}".format(secondsetlowtotalpercent) + ')')
            SetTable.append('second sets v lower rank: ' + str(matches['secondvlowerrank'].sum()) + '\\' + str(
                secondsetlowtotal) + ' (' + "{:.0%}".format(secondsetlowtotalpercent) + ')')            
        except Exception:
            pass       
            SetTable.append('')


    Setdata = '\n'.join(SetTable)
    return Setdata
    #matches=matches.sort_values(by=['tourney_date'], ascending=False)
    #print(matches[['score','winner_name','winner_rank','loser_rank']])


MAINDIR = "C:\\Users\\chris\\OneDrive\\Documents\\GitHub\\tennis_atp\\"
with open(MAINDIR + "atp_players.csv") as pf,  open(MAINDIR + "atp_rankings_current.csv") as rf:
    players = OrderedDict((row[0], row) for row in csv.reader(pf))
    rankings = csv.reader(rf)
    top100 = []
    for i in islice(rankings, None, 100):
        if i[0] != 'ranking_date':
            name = players.get(i[2])[1] + ' ' + players.get(i[2])[2]
            top100.append(name)


allmatcheslist = []

atpmatches = readATPMatches(
    "C:\\Users\\chris\\OneDrive\\Documents\\GitHub\\tennis_atp")
qatpmatches = readChall_QATPMatches(
    "C:\\Users\\chris\\OneDrive\\Documents\\GitHub\\tennis_atp")
wtamatches = readWTAMatches(
    "C:\\Users\\chris\\OneDrive\\Documents\\GitHub\\tennis_wta")
itfmatches = readITFMatches(
    "C:\\Users\\chris\\OneDrive\\Documents\\GitHub\\tennis_atp")
allmatcheslist.append(atpmatches)
allmatcheslist.append(qatpmatches)
allmatcheslist.append(wtamatches)
allmatcheslist.append(itfmatches)
allmatches = pd.concat(allmatcheslist)

#Surface = input('Surface:')


def results(allmatches, Surface, name,opprank):
    tabledata=[]
    try:
        SetData = setstats(allmatches, Surface, name,opprank)
        tabledata.append(SetData)
    except Exception:
        pass 
        tabledata.append('')      
    poo = geth2hforplayer(allmatches, name)
    wins = 0
    losses = 0
    winsvhigherrank = 0
    winsvlowerrank = 0
    lossesvhigherrank = 0
    lossesvlowerrank = 0
    for p in reversed(poo):
        if p[2] == Surface:
            if p[3] == 'Win':
                wins = wins+1
                if p[5] > p[6]:
                    winsvhigherrank = winsvhigherrank+1
                elif p[5] < p[6]:
                    winsvlowerrank = winsvlowerrank+1
            else:
                losses = losses+1
                if p[5] > p[6]:
                    lossesvhigherrank = lossesvhigherrank+1
                elif p[5] < p[6]:
                    lossesvlowerrank = lossesvlowerrank+1
    total = wins+losses
    winpercent = (wins/total)
    try:
        vshigherrankpercentage = (
            winsvhigherrank/(winsvhigherrank+lossesvhigherrank))
        vslowerrankpercentage = (
            winsvlowerrank/(winsvlowerrank+lossesvlowerrank))

        #print("Record: " + str(wins) + '\\' + str(total) +
        #      ' (' + "{:.0%}".format(winpercent) + ')')
        tabledata.append("Record: " + str(wins) + '\\' + str(total) +
            ' (' + "{:.0%}".format(winpercent) + ')')
        if opprank == 'Higher':
        #    print("vs Higher Rank: " + str(winsvhigherrank) + '\\' + str(winsvhigherrank +
        #        lossesvhigherrank) + ' (' + "{:.0%}".format(vshigherrankpercentage) + ')')
            tabledata.append("vs Higher Rank: " + str(winsvhigherrank) + '\\' + str(winsvhigherrank +
                lossesvhigherrank) + ' (' + "{:.0%}".format(vshigherrankpercentage) + ')')

        else:        
            #print("vs Lower Rank: " + str(winsvlowerrank) + '\\' + str(winsvlowerrank +
            #    lossesvlowerrank) + ' (' + "{:.0%}".format(vslowerrankpercentage) + ')')
            tabledata.append("vs Lower Rank: " + str(winsvlowerrank) + '\\' + str(winsvlowerrank +
                lossesvlowerrank) + ' (' + "{:.0%}".format(vslowerrankpercentage) + ')')
    except Exception:
        pass
    data = '\n'.join(tabledata)
    return data

def ValidName(name):
    Valid=False
    name = name.split(' ')
    inFirstName = name[0]
    if len(name) > 2:
        inLastName = name[1] + ' ' + name[2]
    else:
        inLastName = name[1] 
    MAINDIR = "C:\\Users\\chris\\OneDrive\\Documents\\GitHub\\tennis_atp\\"
    with open(MAINDIR + "atp_players.csv") as pf,  open(MAINDIR + "atp_rankings_current.csv") as rf:
        players = OrderedDict((row[0], row) for row in csv.reader(pf))
        for key,value in players.items():
            firstname = value[1]
            lastname = value[2]
            if firstname == inFirstName and lastname == inLastName:
                Valid = True
    MAINDIR = "C:\\Users\\chris\\OneDrive\\Documents\\GitHub\\tennis_wta\\"
    with open(MAINDIR + "wta_players.csv") as pf,  open(MAINDIR + "wta_rankings_current.csv") as rf:
        players = OrderedDict((row[0], row) for row in csv.reader(pf))
        for key,value in players.items():
            firstname = value[1]
            lastname = value[2]
            if firstname == inFirstName and lastname == inLastName:
                Valid = True            
    return Valid

def MatchDataExists(allmatches,Surface,name):
    Valid=False
    """for a player calculates specific set statistics"""
    atpmatches = allmatches
    matches = atpmatches[(atpmatches['winner_name'] == name)
                         | (atpmatches['loser_name'] == name)]

    matches = matches[matches['surface'] == Surface]
    matches = matches[~matches['score'].str.contains('RET|W').fillna(False)]

    if matches.empty==False:
        Valid = True
    return Valid

#name = 'Petra Kvitova'
#print(ValidName(name))

#print("############")
#print(name)
#print("############")
#if ValidName(name) == True:
#    print(results(allmatches, 'Hard', name,'Lower'))
#name = input('Name 2:')
#print("############")
#print(name)
#print("############")
#results(allmatches, Surface, name)
