#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 12:52:26 2020

@author: abhijith
"""
from app import app
from app import server
import glob
import numpy as np
import dash_html_components as html
import dash_core_components as dcc
import dash_table
from dash.dependencies import Input, Output
import json
import plotly.express as px
import plotly.graph_objs as go
import pandas as pd
from helperfns import *

#LFC_gScorers = pd.read_csv('LFC_gScorers.csv')
#MUFC_gScorers = pd.read_csv('MUTD_gScorers.csv')
df_clubs = pd.read_csv('data/clubnames.csv')
clubnames = df_clubs['Club'].to_list()
clubnames.insert(0,'All Clubs')
maindescr = dcc.Markdown('''
Visualization to contrast **impact** of goal scorers. The data used is premier league goals from 2000-2001 season to 2019-2020
**Disclaimer:** The data shown here is for personal consumption. Please leave 
feedback replying to my twitter profile [Ituralde] <https://twitter.com/Ituralde> and give a follow once you are there :-) 
                         ''')

descriptionTab1 = dcc.Markdown('''
**Description of axis variables**

* **Goals per 90 mins**:  (total goals/total minutes played) X 90
* **Points won (normalised)**: If a player's goal was the final goal and that was the game-defining goal, i.e. leading to a draw (+1 point) or a win (+3 points). 
   * **y-axis**: = total points won/(3*matches played)
* **Size** of the blobs: Total goals
''')

descriptionTab2 = dcc.Markdown('''
**Description of axis variables**

* **Goals per 90 mins**:  (total goals/total minutes played) X 90
* **Game-Changing Goals per appearance**: A game-changing goal is the one that takes the lead for the team of ties the score for the team. The goal need not define the end result of the game.
    * **y-axis** (Game-changing goals/Number of appearances for the club)
* **Size** of the blobs: Total goals
''')

selectclubtxt = dcc.Markdown('''#### Select Club ''')
mingoalstxt = dcc.Markdown('''**Minimum Goals**''')
clubseltxt = dcc.Markdown('''**Club(s) Selected**''')

tab_selected_style = {
    'borderTop': '1px solid #d6d6d6',
    'borderBottom': '1px solid #d6d6d6',
    'backgroundColor': 'black',
    'color': 'white',
    'padding': '6px'
}

app.layout = html.Div([
    html.Div(children=[html.H1(children=f'Goal scorers of 21st century'),maindescr]),
    html.Div(children=selectclubtxt),    
    html.Div([
    dcc.Dropdown(id='clubname-dropdown',
                 options=[{'label': i, 'value': i} for i in clubnames],
                 value='Liverpool FC')]),
    html.Div(children=clubseltxt),    
    html.Div(id='club-display'),
    html.Br(),
    html.Div([                 
    html.Div(id='slider-display'),
    dcc.Slider(id='min-goal-slider', min=1, max=30,value=15,
               step=None,
               marks={goals: str(goals) for goals in range(1,31)}),
    ]),
    html.Br(),
    dcc.Tabs([
        dcc.Tab(label='Points Won for Team',selected_style=tab_selected_style,
            children=[
            dcc.Graph(id='gper90-v-ptsnorm-graph'),
            descriptionTab1,
            dcc.Dropdown(id='players-dropdown'),
            dash_table.DataTable(id='player-goals')
            ]),
        dcc.Tab(label='Game Changing Goals for Team',selected_style=tab_selected_style,
            children=[
            dcc.Graph(id='gdper90-v-gcgoalspct-graph'),
            descriptionTab2
            ])
        ]),
    ])

@app.callback(
    Output('min-goal-slider','max'),
    Output('min-goal-slider','value'),
    Output('club-display','children'),
    Input('clubname-dropdown','value')
    )
def get_goaldata(clubname):
    goalScorersAll = pd.read_csv('allEPLgoalScorers.csv')
    if 'All Clubs' not in clubname:
        goalScorers = goalScorersAll[goalScorersAll['Club'].str.contains(clubname)]
    else:
        goalScorers = goalScorersAll
    maxGoals = goalScorers['Goals'].max()
    clubselected = clubname
    if maxGoals<30:
        defval = int(maxGoals/2)
    else:
        defval = 15
        maxGoals = 30
    return maxGoals,defval,clubselected

@app.callback(
    Output('gper90-v-ptsnorm-graph', 'figure'),
    Output('gdper90-v-gcgoalspct-graph','figure'),
    Output('slider-display','children'),
    Input('min-goal-slider','value'),
    Input('club-display','children')
    )
def update_plot(minGoals,clubselected):
    displaystr = f'Minimum Goals: {minGoals}'
    goalScorersAll = pd.read_csv('allEPLgoalScorers.csv')

    
    if 'All Clubs' not in clubselected:
        goalScorers = goalScorersAll[goalScorersAll['Club'].str.contains(clubselected)]
    else:
        goalScorers = goalScorersAll
    goalScorers = goalScorers[goalScorers['Goals']>=minGoals]
    goalScorers.sort_values(by='Goals',ascending=False,inplace=True)
    goalScorers.loc[:,'Goals'] = pd.to_numeric(goalScorers.loc[:,'Goals'])
    goalScorers.loc[:,'GCgoals'] = pd.to_numeric(goalScorers.loc[:,'GCgoals'])
    goalScorers.loc[:,'Appearances'] = pd.to_numeric(goalScorers.loc[:,'Appearances'])
    goalScorers.loc[:,'Minutes'] = pd.to_numeric(goalScorers.loc[:,'Minutes'])
    goalScorers.loc[:,'GoalsPer90'] = 90*(goalScorers.loc[:,'Goals']/goalScorers.loc[:,'Minutes'])
    goalScorers.loc[:,'PointsNorm'] = goalScorers.loc[:,'Points']/(3*goalScorers.loc[:,'Appearances'])
    goalScorers.loc[:,'GCgoalsPCT'] = goalScorers.loc[:,'GCgoals']/goalScorers.loc[:,'Goals']    
    goalScorers.loc[:,'GCgoalsPapp'] = goalScorers.loc[:,'GCgoals']/goalScorers.loc[:,'Appearances']    
    
    goalScorersAll.loc[:,'PointsNorm'] = goalScorersAll.loc[:,'Points']/(3*goalScorersAll.loc[:,'Appearances'])
    goalScorersAll.loc[:,'GoalsPer90'] = 90*(goalScorersAll.loc[:,'Goals']/goalScorersAll.loc[:,'Minutes'])
    gsDF = goalScorersAll[goalScorersAll['Goals']>=minGoals]
    maxptsall = gsDF['PointsNorm'].max()
    maxgp90all = gsDF['GoalsPer90'].max()
    maxgoalsAll = gsDF['Goals'].max()
    maxGCgoalsAll = gsDF['GCgoals'].max()
    
    maxpts = goalScorers['PointsNorm'].max()    
    maxgp90 = goalScorers['GoalsPer90'].max()
    maxapps = goalScorers['Appearances'].max()
    maxgcPapp = goalScorers['GCgoalsPapp'].max()
    
    x_range = np.arange(0,maxgp90+0.1,0.05)
    x_range = x_range.tolist()
    y_range_max = maxptsall*np.ones(len(x_range))
    y_range_max = y_range_max.tolist()
        
    if 'All Clubs' not in clubselected:        
        fig = px.scatter(goalScorers,x='GoalsPer90',y='PointsNorm',color='Name',
                     size='Goals',size_max=40)
        fig1 = px.scatter(goalScorers,x='GoalsPer90',y='GCgoalsPapp',color='Name',
                     size='Goals',size_max=40)
    else:
        fig = px.scatter(goalScorers,x='GoalsPer90',y='PointsNorm',color='Club',hover_name='Name',
                     size='Goals',size_max=40) 
        fig1 = px.scatter(goalScorers,x='GoalsPer90',y='GCgoalsPapp',color='Club',hover_name='Name',
                     size='Goals',size_max=40)
    
    fig.update_layout(xaxis_title='Goals per 90 mins',yaxis_title='Points won for team (normalised)',
                      xaxis=dict(range=[0,maxgp90all+0.1],tickmode='linear',tick0=0,dtick=0.1),
                      yaxis=dict(range=[-0.1,maxptsall+0.1],tickmode='linear',tick0 = 0,dtick=0.1))
    fig1.update_layout(xaxis_title='Goals per 90 mins',yaxis_title='Game-Changing Goals per Appearance',
                      xaxis=dict(range=[0,maxgp90+0.1],tickmode='linear',tick0=0,dtick=0.1),
                       yaxis=dict(range=[0,maxgcPapp+0.1],tickmode='linear',tick0 = 0,dtick=0.1))
    return fig,fig1,displaystr

@app.callback(
    Output('players-dropdown','options'),
    Output('players-dropdown','value'),
    Input('min-goal-slider','value'),
    Input('clubname-dropdown','value')
    )
def playerdropdown(minGoals,clubselected):
    goalScorersAll = pd.read_csv('allEPLgoalScorers.csv')

    
    if 'All Clubs' not in clubselected:
        goalScorers = goalScorersAll[goalScorersAll['Club'].str.contains(clubselected)]
    else:
        goalScorers = goalScorersAll
    goalScorers = goalScorers[goalScorers['Goals']>=minGoals]
    
    playernames = goalScorers['Name'].tolist()
    options_ret = [{'label':i, 'value':i} for i in playernames]
    value_ret = playernames[0]
    return options_ret,value_ret

@app.callback(
    Output('player-goals','columns'),
    Output('player-goals','data'),
    Input('players-dropdown','value'),
    Input('clubname-dropdown','value')
    )
def update_table(playername,clubselected):
    goaleventsDB = pd.read_csv('epl_goalevents_2000_2019.csv')
    if 'All Clubs' not in clubselected:
        playeridx = (goaleventsDB['Player']==playername) & (goaleventsDB['TeamFor']==clubselected)
    else:
        playeridx = (goaleventsDB['Player']==playername)
    playergoals = goaleventsDB[playeridx]
    
    coulumnlist = ['Date','Season','TeamFor','TeamAga','Venue','Time','Score','FTScore','PointsWon']
    columns=[{"name": i, "id": i} for i in coulumnlist]
    playergoalsdict = playergoals.to_dict('records')
    return columns,playergoalsdict
if __name__ == '__main__':
    app.run_server(debug=True)