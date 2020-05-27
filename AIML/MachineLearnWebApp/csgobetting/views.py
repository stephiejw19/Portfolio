from django.shortcuts import render
from csgobetting import queries
from csgobetting import important
from csgobetting import predict
import numpy as np
import json

from django.template import Context, RequestContext
from django.http import JsonResponse

def get_prediction(request):
    team1=request.GET.get('team1')
    team2=request.GET.get('team2')
    datetime=request.GET.get('datetime')
    
    result, win, loss = predict.get_prediction(team1, team2, datetime,
                                    min_odds=0.2,
                                    lookback=12,
                                    lags=1,
                                    rolling_w=3,
                                    min_games=None,
                                    verbose=False,
                                    debug=False,
                                    divide=False,
                                    hypothesis_test=False,
                                    confidence=True)
    
    
    context = {
        'result': str(result),
        'team1': team1,
        'team2': team2,
        'datetime': datetime,
        'team1_chance': win, 
        'team2_chance': loss
    }

    return(JsonResponse(context))# render(context, context_instance=RequestContext(request))

def parse_date(date):
    return(':'.join(str(date).split(':')[:-1]))

def calculate_net_change(series):
    #print(series.correct)
    if int(series.skip_bet) == 1:
        return(0)
    elif int(series.correct) != 1:
        return(-1 * series.amount)
    else:
        if series.HomeTeamName == series.bet_on:
            return((series.home_odds-1)*series.amount)
        else:
            return((series.away_odds-1)*series.amount)

def index(request):
    """View function for home page of site."""
    context = {}
    df = queries.get_predicted_matches()
    
    df['StartTime'] = df['StartTime'].apply(parse_date)
    context['matches'] = list(df.T.to_dict().values())
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def history(request):
    """View function for home page of site."""
    context = {}
    df = queries.get_prediction_results()
    df['net_change'] = df.apply(calculate_net_change, axis=1).cumsum()
    
    context['results'] = list(df.T.to_dict().values())
    context['labels'] = list(df['StartTime'].values)
    
    #index = list((df['StartTime'].astype(np.int64) / int(1e6)).values)
    #context['data'] = '['+','.join(['{t: new Date("' + str(df['StartTime'].values[i]).replace('T',' ') + '"), y: ' + str(df['net_change'].iloc[i]) + "}" for i in range(df.shape[0])])+']'
    
    data = []
    for i in range(df.shape[0]):
        entry = dict()
        entry['x'] = str(df['StartTime'].values[i])
        entry['y'] = df['net_change'].values[i]
        data.append(entry)
        
    context['data'] = json.dumps(data)
    
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'history.html', context=context)

def players(request):
    """View function for home page of site."""
    context = {}
    context['joke'] = important.get_joke()
    # Render the HTML template index.html with the data in the context variable
    return render(request, 'wildbot.html', context=context)

    # Render the HTML template index.html with the data in the context variable

