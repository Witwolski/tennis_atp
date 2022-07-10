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

def readChall_QATPMatches(dirname):
    """reads Challenger level + ATP Q matches but does not parse time into datetime objects"""
    allFiles = glob.glob(dirname + "/atp_matches_qual_chall_2021*") + glob.glob(dirname + "/atp_matches_qual_chall_2022*")
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
    allFiles = glob.glob(dirname + "/atp_matches_futures_2021.csv") + glob.glob(dirname + "/atp_matches_futures_2022.csv")
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
    allFiles = glob.glob(dirname + "/atp_matches_2021.csv")+ glob.glob(dirname + "/atp_matches_2022.csv")
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

MAINDIR = "C:\\Users\\chris\\OneDrive\\Documents\\GitHub\\tennis_atp\\"

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
        tabledata.append("Record: " + str(wins) + '\\' + str(total) +
            ' (' + "{:.0%}".format(winpercent) + ')')
        if opprank == 'Higher':
            tabledata.append("vs Higher Rank: " + str(winsvhigherrank) + '\\' + str(winsvhigherrank +
                lossesvhigherrank) + ' (' + "{:.0%}".format(vshigherrankpercentage) + ')')

        else:        
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

#Surface=input('Surface:')
#name = input('Name 1:')
#print(ValidName(name))
#print("############")
#print(name)
#print("############")
#if ValidName(name) == True:
#    print(results(allmatches, Surface, name, opprank='Lower'))
#name = input('Name 2:')
#print("############")
#print(name)
#print("############")
#if ValidName(name) == True:
#    print(results(allmatches, Surface, name,opprank='Higher'))
