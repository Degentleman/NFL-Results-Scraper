#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 20 04:20:00 2018

@author: Degentleman
"""

from urllib.request import urlopen
from bs4 import BeautifulSoup
import pandas as pd
import numpy as np
import statsmodels.api as sm

team_codes = ['atl','buf','car',
              'chi','cin','cle',
              'clt','crd', 'dal', 
              'den','det', 'gnb', 
              'htx','jax', 'kan',
              'mia','min','nor',
              'nwe','nyg', 'nyj',
              'oti','phi','pit',
              'rai','ram','rav',
              'sdg','sea','sfo', 
              'tam','was']

# URL to Format
url_template = "https://www.pro-football-reference.com/teams/{team}/"

# Iterate Player Data Frame for Each Year Specified

nfl_df = pd.DataFrame()

for team in team_codes:
    
    url = url_template.format(team=team)  # get the url
    
    html = urlopen(url)

    soup = BeautifulSoup(html, 'html.parser')

    column_headers = [th.getText() for th in soup.findAll('thead', limit=1)[0].findAll('tr',attrs={'class':''})[0].findAll('th')]
    
    data_rows = soup.findAll('tbody', limit=1)[0].findAll('tr')[0:]

    team_data = [[td.getText() for td in data_rows[i].findAll(['th','td'])] 
    for i in range(len(data_rows))]
    
    # Turn yearly data into a DataFrame
    
    year_df = pd.DataFrame(team_data, columns=column_headers)
    
    year_df = year_df.loc[(year_df['Div. Finish'] !='Overall Rank') & (year_df['Div. Finish'] !='Div. Finish')]
    
    year_df = year_df.infer_objects().reset_index(drop=True)
    
    nfl_df = pd.concat([nfl_df,year_df], axis=0,ignore_index=True)
    
print('All historical data has been scraped.')

points_for = pd.Series(data=np.array(nfl_df['PF'],dtype=int),name='Points For')

points_allowed = pd.Series(data=np.array(nfl_df['PA'],dtype=int),name='Points Allowed')

games_played = pd.Series(data=(np.array(nfl_df['W'],dtype=int)+np.array(nfl_df['L'],dtype=int)+np.array(nfl_df['T'],dtype=int)),name='Games Played')

games_won = pd.Series(data=np.array(nfl_df['W'],dtype=int),name='Games Won')

X = pd.concat([points_for,points_allowed,games_played],axis=1)

y = games_won

model = sm.OLS(y,X).fit()

print(model.summary())

nfl_df.to_csv('NFLHistoricalTeamData.csv')