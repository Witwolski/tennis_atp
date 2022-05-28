import datetime
import requests
from bs4 import BeautifulSoup
import argparse
import datetime
from tabulate import tabulate
import pandas as pd
from Tennis_ITF import *
import openpyxl
import xlsxwriter


def Main(url, current_date,Filter):

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='count', default=0)

    args = parser.parse_args()

    # # Get the current date
    #tomorrow = datetime.datetime.now() + datetime.timedelta(hours=-12)
    #year, month, day = tomorrow.year, tomorrow.month, tomorrow.day
    #current_date = str(year) + '-' + str(month) + '-' + str(day)

    # # ################### MATCH OF THE DAY ###################

    # # Get matchs of the day +1
    #url = 'https://www.tennisexplorer.com/matches/?type=atp-single&year={}&month={}&day={}'.format(year, month, day)
    #url = 'https://www.tennisexplorer.com/matches/?type=wta-single&year={}&month={}&day={}'.format(year, month, day)
    # # Launch the request
    response = requests.get(url)

    # # Analysis with beautifulsoup
    soup = BeautifulSoup(response.content, 'html.parser')

    table = soup.find("table", {"class": "result"})
    table = soup.findAll("table", {"class": "result"})[1]

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
        name = name.replace('Lesya Tsurenko', 'Lesia Tsurenko').replace(
            'Harry Fritz Taylor', 'Taylor Fritz').replace(
                'Carlos Alcaraz', 'Carlos Alcaraz Garfia').replace(
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
                            'Viktoria Azarenka','Victoria Azarenka').replace(
                                'Marco Moroni Gian','Gian Marco Moroni')
        return name.strip().replace('-', ' ') + '(' + player_rank + ')'

    tournament_dict = {
    }

    for i, item in enumerate(tournament_idx_lst[:-1]):

        tournament_name = rows[item].find("td", class_="t-name").text.strip()
        # if 'Next Gen' not in tournament_name and 'ITF' not in tournament_name and 'Future' not in tournament_name and 'Pro' not in tournament_name and 'Tenerife' not in tournament_name and 'Challenger' not in tournament_name and 'challenger' not in tournament_name:
        # if 'Futures' in tournament_name or 'challenger' in tournament_name or 'ITF' in tournament_name:
        if Filter in tournament_name:
            print(tournament_name, i)
            court_type = 'Clay'
            court_type = 'Hard'
            if '' in tournament_name:
                # if "Pro Tennis" in tournament_name or "Futures" in tournament_name or "challenger" in tournament_name:
                #    # if "Pro Tennis" in tournament_name:
                #    continue
                if not tournament_dict.get(tournament_name):
                    tournament_dict[tournament_name] = {}
                    tournament_dict[tournament_name][current_date] = []
                for c in range(item+1, tournament_idx_lst[i+1], 2):
                    tournament_dict[tournament_name][current_date].append(getPlayersFullName(rows[c].find(
                        "td", class_="t-name").a['href']) + ' vs ' + getPlayersFullName(rows[c+1].find("td", class_="t-name").a['href']) + ":" + court_type)

    for key, value in tournament_dict.items():
        datefilename = current_date.replace("-", "")

        with xlsxwriter.Workbook(r"C:\Users\chris\OneDrive\Desktop\Tennis\\" + key + ' ' + datefilename + "_" + court_type + "_ResultsOnly.xlsx") as workbook:
            for i, date in value.items():
                for match in date:
                    Surface = match.split(':')[1]
                    match = match.split(':')[0]
                    players = match.split(' vs ')
                    player1 = players[0].split('(')[0]
                    player2 = players[1].split('(')[0]
                    if (MatchDataExists(allmatches, Surface, player1) == False):
                        print("No Match Data for {}".format(player1))
                    if (MatchDataExists(allmatches, Surface, player2) == False):
                        print("No Match Data for {}".format(player2))
                    if (MatchDataExists(allmatches, Surface, player1) and MatchDataExists(allmatches, Surface, player2)):
                        # if 'Rebeca Pereira' not in players[1].split('(')[0] and 'Rebeca Pereira' not in players[0].split('(')[0] and 'Piros' not in players[1].split('(')[0] and 'Piros' not in players[0].split('(')[0] and 'Marozsan' not in players[1].split('(')[0] and 'Marozsan' not in players[0].split('(')[0] and 'Tomas Barrios Vera Marcelo' not in players[1].split('(')[0] and 'Tomas Barrios Vera Marcelo' not in players[0].split('(')[0] and 'Aleksandar Kovacevic' not in players[1].split('(')[0] and 'Aleksandar Kovacevic' not in players[0].split('(')[0] and 'Kozlov' not in players[1].split('(')[0] and 'Kozlov' not in players[0].split('(')[0] and 'Melzer' not in players[1].split('(')[0] and 'Melzer' not in players[0].split('(')[0] and 'Michael Mmoh' not in players[0].split('(')[0] and 'Michael Mmoh' not in players[1].split('(')[0] and 'Ernesto Escobedo' not in players[1].split('(')[0] and 'Ernesto Escobedo' not in players[0].split('(')[0]:
                        # if 'Moraing' in player2 or 'Moraing' in player1:
                        player1rank = players[0].split('(')[1].replace(')', '')
                        player2rank = players[1].split('(')[1].replace(')', '')
                        #Surface = 'Hard'

                        player1 = players[0].split('(')[0]
                        if int(player1rank) > int(player2rank):
                            opprank = 'Higher'
                        else:
                            opprank = 'Lower'
                        if ValidName(player1) == True:
                            Column1 = results(
                                allmatches, Surface, player1, opprank)
                        else:
                            Column1 = ''

                        player2 = players[1].split('(')[0]

                        if int(player2rank) > int(player1rank):
                            opprank = 'Higher'
                        else:
                            opprank = 'Lower'
                        if ValidName(player2) == True:
                            Column2 = results(
                                allmatches, Surface, player2, opprank)
                        else:
                            Column2 = results(
                                allmatches, Surface, player2, opprank)
                        if (Column1 != '' and Column2 != ''):
                            table = [[players[0], players[1]],
                                     [Column1, Column2]]
                            tab = tabulate(table, headers='firstrow')

                            worksheetname = player1.split(
                                ' ')[1] + '_' + player2.split(' ')[1]
                            worksheet = workbook.add_worksheet(worksheetname)
                            # Add a format to use wrap the cell text.
                            wrap = workbook.add_format({'text_wrap': True})

                            # Increase the row and cell height so the output is clearer.
                            worksheet.set_column('A:B', 50)
                            worksheet.set_row(0, 20)
                            worksheet.set_row(1, 50)

                            for row_num, data in enumerate(table):
                                worksheet.write_row(row_num, 0, data, wrap)


# # Get the current date
tomorrow = datetime.datetime.now() + datetime.timedelta(hours=0)
year, month, day = tomorrow.year, tomorrow.month, tomorrow.day
current_date = str(year) + '-' + str(month) + '-' + str(day)
Filter = 'Aus'
#print('https://www.tennisexplorer.com/matches/?type=atp-single&year={}&month={}&day={}'.format(year, month, day))
#Main('https://www.tennisexplorer.com/matches/?type=atp-single&year={}&month={}&day={}'.format(year, month, day), current_date,Filter)
Main('https://www.tennisexplorer.com/matches/?type=wta-single&year={}&month={}&day={}'.format(year, month, day), current_date,Filter)
