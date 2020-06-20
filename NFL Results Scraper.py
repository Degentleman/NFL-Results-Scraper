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
from scipy import stats

# URL to Format
url_template = "https://www.pro-football-reference.com/years/{year}/games.htm"

# Iterate Player Data Frame for Each Year Specified

nfl_df = pd.DataFrame()

for year in range(2012, 2018):
    
    url = url_template.format(year=year)  # get the url
    
    html = urlopen(url)

    soup = BeautifulSoup(html, 'html.parser')

    column_headers = [th.getText() for th in soup.findAll('thead', limit=1)[0].findAll('th')]
    
    data_rows = soup.findAll('tbody', limit=1)[0].findAll('tr')[0:]

    player_data = [[td.getText() for td in data_rows[i].findAll(['th','td'])] 
    for i in range(len(data_rows))]
    
    # Turn yearly data into a DataFrame
    
    year_df = pd.DataFrame(player_data, columns=column_headers)
    
    year_df = year_df[(year_df.Date !='Playoffs') & (year_df.Week !='WildCard') & (year_df.Week != 'Week' )]
    
    year_df = year_df.infer_objects().reset_index(drop=True)
    
    results = year_df.loc[(year_df.iloc[:,8] != '')]

    winner_pts = np.array(results.iloc[:,8],dtype=int)
    
    loser_pts = np.array(results.iloc[:,9],dtype=int)
    
    spreads = winner_pts-loser_pts
    
    winner_pf = stats.zscore(winner_pts)
    
    loser_pf = stats.zscore(loser_pts)
    
    points_pf = list(winner_pts)+list(loser_pts)
    
    percentile = np.array([stats.norm.cdf(x) for x in stats.zscore(spreads)])
    
    results_df = pd.concat([results,
               pd.DataFrame(data=winner_pf,columns=['Winner Performance']),
               pd.DataFrame(data=loser_pf,columns=['Loser Performance']),
               pd.DataFrame(data=spreads,columns=['Spread']),
               pd.DataFrame(data=percentile,columns=['Spread Prcntl']),
               ],axis=1)
    
    col_len = [x for x in range(results_df.shape[1])]
    
    col_len.remove(7)
    
    results_df = results_df.iloc[:,col_len]
    
    results_df = results_df.rename(columns={list(results_df)[5]:'H/A',
                               list(results_df)[7]:'Pts Scored',
                               list(results_df)[8]:'Pts Allowed',
                               list(results_df)[9]:'Yds Gained',
                               list(results_df)[10]:'TOs',
                               list(results_df)[11]:'Yds Allowed',
                               list(results_df)[12]:'Opp TOs',
                               list(results_df)[13]:'Tm Performance',
                               list(results_df)[14]:'Opp Performance'})
    
    filename = 'NFL {year} Weekly Results.csv'.format(year=year)
    
    results_df.to_csv(filename)
    
    nfl_df = pd.concat([nfl_df,results_df],axis=0)

    print(filename+' has been saved.')
    
print('All results from the specified timeframe have been saved.')

nfl_df = nfl_df.reset_index(drop=True)
