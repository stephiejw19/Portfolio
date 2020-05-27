from csgobetting import queries
from csgobetting import odds_loss_function
import warnings
warnings.filterwarnings("ignore")
import pandas as pd
import numpy as np
from sklearn.metrics import classification_report
from surprise import SVD 
from surprise import Dataset, Reader
from surprise.model_selection import cross_validate, train_test_split
import surprise
import os
import matplotlib.pyplot as plt
import tensorflow as tf
from datetime import datetime
from statsmodels.tsa.vector_ar.var_model import VAR
from random import random
import scipy.stats as st
#committing to get an update#

def monthdelta(date, delta):
    m, y = (date.month+delta) % 12, date.year + ((date.month)+delta-1) // 12
    if not m: m = 12
    d = min(date.day, [31,
        29 if y%4==0 and not y%400==0 else 28,31,30,31,30,31,31,30,31,30,31][m-1])
    return date.replace(day=d,month=m, year=y)

def get_timeseries_for_team(df, team, time=datetime.now(), lookback=1):
    #Create X=[map]([1-hot team 1] + [1-hot team 2]), y=[alphabetically order ratio] style of data
    df = df.loc[np.array(df.index < time) & np.array(df.index > monthdelta(time, -lookback))]
    matches = df.groupby(['match_id',
                          'team_name',
                          'match_datetime']).mean().reset_index(level=1).join(df.groupby(['match_id',
                                                                                          'team_name',
                                                                                          'match_datetime']).mean().reset_index(level=1), lsuffix='_a', rsuffix='_b')
    matches = matches.loc[matches['team_name_a'] != matches['team_name_b']]
    matches.columns = [x.replace('_assists','') for x in matches.columns]
    
    matches = matches.loc[np.array(matches['team_name_a'] == team) + np.array(matches['team_name_b'] == team)]
    
    def sort_team_names(series, team):
        pair = [series['team_name_a'],series['team_name_b']]
        pair.sort()
        #Need to reorder the stats if swapping teams
        if series['team_name_b'] == team:
            #print(pair)
            copy_series = series.copy()
            for col in series.index:
                if '_a' in col:
                    base = col.split('_a')[0]
                    series[col] = copy_series[base+'_b']
                elif '_b' in col:
                    base = col.split('_b')[0]
                    series[col] = copy_series[base+'_a']
        return(series)
    
    matches = matches.apply(sort_team_names, args=[team], axis=1)
    matches = matches.drop_duplicates()
    
    matches = matches.groupby(['match_datetime','team_name_a','team_name_b']).mean()
    matches = matches.reset_index(level=1).reset_index(level=1) 

    matches['win_ratio'] = matches['rounds_won_a']/(matches['rounds_won_b']+matches['rounds_won_a'])

    team_matches = matches.drop(['kills_b', 'headshots_b', 'assists_b', 'flash_b', 
                                      'deaths_b', 'kast_b', 'kd_diff_b', 'adr_b', 'first_kill_diff_b', 
                                      'rating_b', 'pistol_wins_b', 'rounds_won_b', 'rounds_lost_b'], axis=1)
    team_matches.columns = [x.replace('_a','') for x in team_matches.columns]
    
    return(team_matches)

def create_var_results(team_matches, lags=1):
    data = team_matches.to_numpy()
    model = VAR(data)
    model_fit = model.fit(lags, trend='nc')
    yhat = model_fit.forecast_interval(data, 1)
    return(pd.DataFrame([x[0] for x in yhat], index=[['mean', 'lower','upper']], columns=team_matches.columns)['win_ratio'])

def get_prob_success(ci, alpha=0.05, hypothesis_test=True):
    if np.nan in ci:
        return(0)
    if not hypothesis_test:
        return(ci[0])
    sigma = (ci[2]-ci[0])/norm_signif_level(alpha)
    z = (1-ci[0])/sigma
    return(1-st.norm.cdf(z))

def clean_timeseries(team_matches, df, min_games=1, rolling_w=1, categorical=False):
    #if categorical:
    #    team_matches = team_matches
    team_matches = team_matches[team_matches.columns[team_matches.dtypes == float]]
    team_matches = team_matches.dropna(axis=1)
    if rolling_w > 1:
        team_matches = team_matches.rolling(rolling_w).mean()
        team_matches = team_matches.dropna()
    assert(team_matches.shape[0] > min_games), "Not enough rows: " + str(team_matches.shape[0])
    #team_matches = CATEGORICAL 
    team_matches.loc[:, (team_matches != df.iloc[0]).any()]
    assert ('win_ratio' in team_matches.columns),"'win_ratio' not in columns"
    return(team_matches)

def norm_signif_level(alpha=0.05):
    return st.norm.ppf(1 - alpha)

def get_prediction(team_a, team_b, date_time,
                                min_odds=1e-4,
                                lookback=3,
                                lags=1,
                                rolling_w=2,
                                min_games=None,
                                verbose=True,
                                debug=False,
                                divide=True,
                                hypothesis_test=True,
                                confidence=False):
    
    ts = pd.to_datetime(date_time)
    
    df = queries.get_historic_match_data_from_date(date_time,lookback)
    df['match_datetime'] = pd.to_datetime(df['match_datetime'])
    df = df.set_index('match_datetime')
    df = df.sort_index()
    df = df.drop_duplicates()
    
    if not min_games:
        min_games = max(lags,rolling_w) + 1

    chance_of_victory = 0
    chance_win = np.nan
    chance_loss = np.nan

    try:
        team_matches = get_timeseries_for_team(df, team_a, time=ts, lookback=lookback).sort_index()
        team_matches = clean_timeseries(team_matches, df, min_games, rolling_w=rolling_w)
        chance_win  = get_prob_success(create_var_results(team_matches, lags=lags), hypothesis_test=hypothesis_test)

        team_matches = get_timeseries_for_team(df, team_b, time=ts, lookback=lookback).sort_index()
        team_matches = clean_timeseries(team_matches, df, min_games, rolling_w=rolling_w)
        chance_loss = get_prob_success(create_var_results(team_matches, lags=lags), hypothesis_test=hypothesis_test)


    except AssertionError as e:
        if debug: 
            print(str(e) + "\n" + str(ts) + " '" + team_a + "' vs '" + team_b + "' doesn't have enough matches")

    if divide:
        chance_of_victory = (chance_win / chance_loss)
        should_bet = (np.abs(chance_of_victory) < min_odds and chance_of_victory < 1) or (1/np.abs(chance_of_victory) < min_odds and chance_of_victory > 1)
        bet_on = 0 if chance_of_victory > 1 else 1
    else:
        chance_of_victory = (chance_win - chance_loss)
        should_bet = np.abs(chance_of_victory) > min_odds
        bet_on = 0 if chance_of_victory > 0 else 1

    if np.isnan(chance_of_victory):
        should_bet = False

    prediction = [[0,0,0]]
    if not should_bet:
        prediction[0][2] = 1
    else:
        prediction[0][bet_on] = 1
            
    if confidence:
        return(prediction, chance_win, chance_loss)
    return(prediction)

