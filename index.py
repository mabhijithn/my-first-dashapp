#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 12:52:26 2020

@author: abhijith
"""
from app import app
from app import server
import glob
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import json
import plotly.express as px
import pandas as pd
from helperfns import *

#LFC_gScorers = pd.read_csv('LFC_gScorers.csv')
#MUFC_gScorers = pd.read_csv('MUTD_gScorers.csv')
df_clubs = pd.read_csv('data/clubnames.csv')
clubnames = df_clubs['Club'].to_list()
clubnames.insert(0,'All Clubs')

description = dcc.Markdown('''
Visualization to contrast **impact** of goal scorers. The data used is premier league goals from 2000-2001 season to 2019-2020

**Description of axis variables**

* **Goals per 90 mins**:  (total goals/total minutes played) X 90
* **Points won (normalised)**: If a player's goal was the final goal and that was the game-defining goal, i.e. leading to a draw (+1 point) or a win (+3 points). 
    * normalised points = total points won/(3*matches played)
* **Size** of the blobs: Total goals
''')

selectclubtxt = dcc.Markdown('''#### Select Club ''')
mingoalstxt = dcc.Markdown('''**Minimum Goals**''')
clubseltxt = dcc.Markdown('''**Club(s) Selected**''')
# app.layout = html.Div(children=[
#     html.H1(children=f'Goal scorers of 21st century'),

#     html.Div(children=description),
#     dcc.Dropdown(id='clubname-dropdown',
#                  options=[{'label': i, 'value': i} for i in clubnames],
#                  value='Liverpool'),                 
#     dcc.Slider(id='min-goal-slider', min=5, max=30,value=15),
#     dcc.Graph(
#         id='gper90-v-ptsnorm-graph',
#     )
# ])

app.layout = html.Div([
    html.Div(children=[html.H1(children=f'Goal scorers of 21st century'),html.Div(children=description)]),
    html.Br(),
    html.Div(children=selectclubtxt),    
    html.Div([
    dcc.Dropdown(id='clubname-dropdown',
                 options=[{'label': i, 'value': i} for i in clubnames],
                 value='Liverpool FC')]),
    html.Div(children=clubseltxt),    
    html.Div(id='club-display'),
    html.Br(),html.Br(),
    html.Br(),
    html.Div([                 
    dcc.Slider(id='min-goal-slider', min=1, max=30,value=15,
               step=None,
               marks={goals: str(goals) for goals in range(1,31)}),
    html.Div(children=mingoalstxt),
    html.Div(id='slider-display')
    ]),
    html.Br(),
    dcc.Graph(
        id='gper90-v-ptsnorm-graph'
    )])

@app.callback(
    Output('min-goal-slider','max'),
    Output('min-goal-slider','value'),
    Output('club-display','children'),
    Input('clubname-dropdown','value')
    )
def get_goaldata(clubname):
    playerfiles = glob.glob('data/players_updated/*.json')
    goalScorers,maxGoals = getgoalscorers(playerfiles,clubname)
    if 'All Clubs' in clubname:
        goalScorers.to_csv('allEPLgoalScorers.csv')
    else:
        goalScorers.to_csv('goalScorers.csv')
    clubselected = clubname
    if maxGoals<30:
        defval = int(maxGoals/2)
    else:
        defval = 15
        maxGoals = 30
    return maxGoals,defval,clubselected

@app.callback(
    Output('gper90-v-ptsnorm-graph', 'figure'),
    Output('slider-display','children'),
    Input('min-goal-slider','value'),
    Input('club-display','children')
    )
def update_plot(minGoals,clubselected):
    displaystr = f'{minGoals}'
    if 'All Clubs' not in clubselected:
        goalScorers = pd.read_csv('goalScorers.csv')
    else:
        goalScorers = pd.read_csv('allEPLgoalScorers.csv')
    goalScorers = goalScorers[goalScorers['Goals']>=minGoals]
    goalScorers.sort_values(by='Goals',ascending=False,inplace=True)
    goalScorers['Goals'] = pd.to_numeric(goalScorers['Goals'])
    goalScorers['GCgoals'] = pd.to_numeric(goalScorers['GCgoals'])
    goalScorers['Appearances'] = pd.to_numeric(goalScorers['Appearances'])
    goalScorers['Minutes'] = pd.to_numeric(goalScorers['Minutes'])
    goalScorers.loc[:,'GoalsPer90'] = 90*(goalScorers.loc[:,'Goals']/goalScorers.loc[:,'Minutes'])
    goalScorers.loc[:,'PointsNorm'] = goalScorers.loc[:,'Points']/(3*goalScorers.loc[:,'Appearances'])
        
    maxpts = goalScorers['PointsNorm'].max()
    
    if 'All Clubs' not in clubselected:        
        fig = px.scatter(goalScorers,x='GoalsPer90',y='PointsNorm',color='Name',
                     size='Goals',size_max=40)
    else:
        fig = px.scatter(goalScorers,x='GoalsPer90',y='PointsNorm',color='Club',hover_name='Name',
                     size='Goals',size_max=40)    
    fig.update_layout(xaxis_title='Goals per 90 mins',yaxis_title='Points won for team (normalised)',
                      yaxis=dict(range=[-0.1,maxpts+0.1],tickmode='linear',tick0 = 0,dtick=0.1))
    return fig,displaystr

if __name__ == '__main__':
    app.run_server(debug=True)