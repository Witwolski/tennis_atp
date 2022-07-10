import sys
import csv
from bs4 import BeautifulSoup
import re
import argparse
import requests

url = r"https://www.betexplorer.com/tennis/"
parser = argparse.ArgumentParser()
parser.add_argument('-v', '--verbose', action='count', default=0)

args = parser.parse_args()
response = requests.get(url)

# # Analysis with beautifulsoup
soup = BeautifulSoup(response.content, 'html.parser')

table = soup.find("table", {"class": "table-main only12 js-nrbanner-t"})


#table = soup.findAll("table", {"class": "result"})[1]
check=0
if(check == 1):
    table = soup.find("table", {"class": "result"})
table_body = table.find('tbody')

rows = table_body.find_all('tr')
tournament_idx_lst = []
for i, row in enumerate(rows):
    if '<th class="h-text-left"' in str(row):
        t_name = row.find("a", {"class": "table-main__tournament table-main__tournament--tennis"}).text
        tournament_idx_lst.append(i)

tournament_idx_lst.append(len(rows))
