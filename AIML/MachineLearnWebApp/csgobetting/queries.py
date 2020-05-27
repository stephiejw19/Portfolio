import pyodbc
import pandas as pd
import numpy as np

def create_connection():
    return(pyodbc.connect('Driver={ODBC Driver 17 for SQL Server};'
                      'Server=csgobetting.database.windows.net;'
                      'Database=csgobetting;'
                      'UID=csgobetting;'
                      'PWD=Password1'))


def get_historic_match_data():
    conn = create_connection()

    #cursor = conn.cursor()
    sql = '''select * from dbo.player_stats;'''

    return(pd.read_sql(sql, conn))

def get_all_data():
    conn = create_connection()

    #cursor = conn.cursor()
    sql = '''select * from dbo.bets as bets 
                        INNER JOIN dbo.markets as mk 
                        ON (bets.Id = mk.MatchId)
                        INNER JOIN dbo.odds as odds
                        on (odds.MarketId = mk.Id)
                        INNER JOIN dbo.player_stats as ps
                        on ((odds.Name like '%' + ps.team_name + '%' or ps.team_name like '%' + odds.Name + '%') and ps.match_datetime = bets.StartTime) where bets.LeagueId='00000000-0000-0000-0000-000000000cd6' ;'''
    #cursor.execute(sql)

    return(pd.read_sql(sql, conn))


def get_all_data_by_id(match_id):
    conn = create_connection()

    #cursor = conn.cursor()
    sql = '''select * from dbo.odds where MatchId in (select Id from dbo.bets where exists (select match_datetime from dbo.player_stats where match_datetime = dbo.bets.StartTime and  team_name = Name and match_id = ''' + str(match_id) + ''')) and MarketId in (select Id from dbo.markets where Name = 'Match Winner')'''
    #cursor.execute(sql)

    return(pd.read_sql(sql, conn))


def run_custom_query(sql):
    conn = create_connection()

    cursor = conn.cursor()
    #cursor.execute(sql)

    return(pd.read_sql(sql, conn))

def sort_team_names(series):
    pair = [series['team_name_a'],series['team_name_b']]
    pair.sort()
    #Need to reorder the stats if swapping teams
    if series['team_name_b'] == pair[0]:
        copy_series = series.copy()
        for col in series.index:
            if '_a' in col:
                base = col.split('_a')[0]
                series[col] = copy_series[base+'_b']
            elif '_b' in col:
                base = col.split('_b')[0]
                series[col] = copy_series[base+'_a']
    return(series)
    
def pull_data_in_loss_function_format():
    df2 = get_all_data()
    
    #Count how many matches
    print("# games: " + str(df2[['match_id','rounds_won','rounds_lost']].groupby(['match_id']).mean().shape[0]))
    
    df2['match_datetime'] = pd.to_datetime(df2['match_datetime'])
    df2 = df2.set_index('match_datetime')
    df2 = df2.sort_index()
    df2 = df2.drop_duplicates()
    df2.Value = df2.Value.apply(float)
    df2 = df2.loc[:,~df2.columns.duplicated()]
    
    matches2 = df2.groupby(['MatchId','match_datetime','match_id','map','team_name']).mean().reset_index(level=4).join(df2.groupby(['MatchId','match_datetime','match_id','map','team_name']).mean().reset_index(level=4), lsuffix='_a', rsuffix='_b')
    matches2 = matches2.loc[matches2['team_name_a'] != matches2['team_name_b']]
    
    #stupid little bug with substrings since '_a' and '_b' are both in flash_assists_b
    matches2.columns = [x.replace('_assists','') for x in matches2.columns]
    
    matches2 = matches2.apply(sort_team_names, axis=1)
    matches2 = matches2.drop_duplicates()

    matches2['won'] = np.round(matches2['rounds_won_a']/(matches2['rounds_won_a'] + matches2['rounds_won_b']))
    matches2['lost'] = 1-matches2['won']
    return(matches2.reset_index().set_index(['MatchId', 'match_datetime','team_name_a','team_name_b', 'match_id','map'])[['won','lost','Value_a','Value_b']])


def get_upcoming_matches():
    sql = '''select tor.Name as tournament, bets.HomeTeamName, bets.HomeTeamId, bets.AwayTeamName, bets.AwayTeamId, bets.StartTime, bets.LeagueId, bets.isLive, odds.Value as home_odds, odds2.Value as away_odds
            from (select * from dbo.bets where bets.StartTime > GETDATE() and bets.LeagueId='00000000-0000-0000-0000-000000000cd6') as bets 
            INNER JOIN dbo.tournaments as tor 
            ON (bets.tournament = tor.Id)
            INNER JOIN (select * from dbo.markets where Name = 'Match Winner') as mk 
            ON (bets.Id = mk.MatchId)
            INNER JOIN dbo.odds as odds
            on (odds.MarketId = mk.Id and odds.Name = bets.HomeTeamName)
            INNER JOIN dbo.odds as odds2
            on (odds2.MarketId = mk.Id and odds2.Name = bets.AwayTeamName)
            order by bets.StartTime asc;'''
    
    return(run_custom_query(sql))

def get_upcoming_matches_with_predictions():
    sql = '''select tor.Name as tournament, bets.HomeTeamName, bets.HomeTeamId, bets.AwayTeamName, bets.AwayTeamId, bets.StartTime, bets.LeagueId, bets.isLive, odds.Value as home_odds, odds2.Value as away_odds
            from (select * from dbo.bets where bets.StartTime > GETDATE() and bets.LeagueId='00000000-0000-0000-0000-000000000cd6') as bets 
            INNER JOIN dbo.tournaments as tor 
            ON (bets.tournament = tor.Id)
            INNER JOIN (select * from dbo.markets where Name = 'Match Winner') as mk 
            ON (bets.Id = mk.MatchId)
            INNER JOIN dbo.odds as odds
            on (odds.MarketId = mk.Id and odds.Name = bets.HomeTeamName)
            INNER JOIN dbo.odds as odds2
            on (odds2.MarketId = mk.Id and odds2.Name = bets.AwayTeamName)
            order by bets.StartTime asc;'''
    
    return(run_custom_query(sql))

def get_prediction_results():
    sql = '''select StartTime, HomeTeamName, AwayTeamName, amount, bet_on, confidence, skip_bet, correct, home_odds, away_odds from dbo.predictions where StartTime < GETDATE() order by StartTime asc'''
    
    return(run_custom_query(sql))

def get_historic_match_data_from_date(date, lookback):
    conn = create_connection()

    #cursor = conn.cursor()
    sql = '''select * from dbo.player_stats where match_datetime >  DATEADD(m,-''' + str(lookback) + ''',\'''' + str(date) + '''') and match_datetime < \'''' + str(date) + '''';'''

    return(pd.read_sql(sql, conn))


def get_predicted_matches():
    sql = '''select * from dbo.predictions where StartTime > GETDATE() and LeagueId='00000000-0000-0000-0000-000000000cd6' order by StartTime asc;'''
    
    return(run_custom_query(sql))



