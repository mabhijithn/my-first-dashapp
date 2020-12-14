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
* **Points won**: If a player's goal was the final goal and that was the game-defining goal, i.e. leading to a draw (+1 point) or a win (+3 points). 
   * **y-axis**: = total points won
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
            html.Br(),
            dcc.RadioItems(id='radio-pointsaxis',
                options = [
                 {'label':'(y-axis) Points Won','value':'PointsWon'},
                 {'label':'(y-axis) Points won normalised by matches played','value':'PointsNorm'}                
                ],
                value = 'PointsWon'
                ),
            dcc.Graph(id='gper90-v-ptsnorm-graph'),
            descriptionTab1,
            dcc.Markdown('''
                         ### Goal List of Players 
                         #### **(Point-Winning goals highlighted)**
                         ##### Select Player from the dropdown below
                         '''),
            dcc.Dropdown(id='players-dropdown'),
            dash_table.DataTable(id='points-goals',
            style_cell={'textAlign': 'left'},
            style_data_conditional=[
            {
                'if': {
                    'filter_query': '{PointsWon} > 0',
                    },
                'backgroundColor': '#FF4136',
                'color': 'white'
            },
            ])                           
            ]),
        dcc.Tab(label='Game Changing Goals for Team',selected_style=tab_selected_style,
            children=[
            dcc.RadioItems(id='radio-gcgoalaxis',
                options = [                 
                 {'label':'(y-axis) Game-changing goals (normalised)','value':'GCgoalsPapp'},
                 {'label':'(y-axis) Game-changing goals','value':'GCGoals'}
                ],
                value = 'GCgoalsPapp'
                ),
            dcc.Graph(id='gdper90-v-gcgoalspct-graph'),
            descriptionTab2,
            dcc.Markdown('''
                         ### Goal List of Players 
                         #### **(Game-changing goals highlighted)**
                         ##### Select Player from the dropdown below
                         '''),
            dcc.Dropdown(id='players-dropdown-2'),
            dash_table.DataTable(id='gc-goals',
            style_cell={'textAlign': 'left'},
            style_data_conditional=[
            {
                'if': {
                    'filter_query': '{GCGoal} eq "Yes"',
                    },
                'backgroundColor': '#FF4136',
                'color': 'white'
            },
            ])
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
    Input('club-display','children'),
    Input('radio-pointsaxis','value'),
    Input('radio-gcgoalaxis','value')
    )
def update_plot(minGoals,clubselected,pointsaxis,gcgoalsaxis):
    displaystr = f'Minimum Goals: {minGoals}'
    goalScorersAll = pd.read_csv('allEPLgoalScorers.csv')
    playerstatsAll = pd.read_csv('epl_aggregate_appearances_with_goals_allplayers_2000_2020.csv')
    patternstr = '[a-zA-z_äöüÄÖÜùûüÿàâæéèêëïîô]+'
    
    if 'All Clubs' not in clubselected:
        goalScorers = goalScorersAll[goalScorersAll['Club'].str.contains(clubselected)]
        playerstats = playerstatsAll[playerstatsAll['Club']==clubselected]
    else:
        goalScorers = goalScorersAll
        playerstats = playerstatsAll
        
    datatoplot = playerstats[playerstats['Goals']>=minGoals]
    datatoplot['Surname'] = datatoplot['Name'].str.extract(r' ([a-zA-z_äöüÄÖÜŠùûüÿàáâćæéèêëïîíôšž ]+)')
    datatoplot.sort_values(by='Goals',ascending=False,inplace=True)
    datatoplot.loc[:,'Goals'] = pd.to_numeric(datatoplot.loc[:,'Goals'])
    datatoplot.loc[:,'GCGoals'] = pd.to_numeric(datatoplot.loc[:,'GCGoals'])
    datatoplot.loc[:,'Appearances'] = pd.to_numeric(datatoplot.loc[:,'Appearances'])
    datatoplot.loc[:,'Minutes'] = pd.to_numeric(datatoplot.loc[:,'Mins'])
    datatoplot.loc[:,'GoalsPer90'] = 90*(datatoplot.loc[:,'Goals']/datatoplot.loc[:,'Mins'])
    datatoplot.loc[:,'PointsNorm'] = datatoplot.loc[:,'PointsWon']/(datatoplot.loc[:,'Appearances'])
    datatoplot.loc[:,'GCgoalsPCT'] = datatoplot.loc[:,'GCGoals']/datatoplot.loc[:,'Goals']    
    datatoplot.loc[:,'GCgoalsPapp'] = datatoplot.loc[:,'GCGoals']/datatoplot.loc[:,'Appearances'] 
    playerstatsAll.loc[:,'PointsNorm'] = playerstatsAll.loc[:,'PointsWon']/(3*playerstatsAll.loc[:,'Appearances'])
    playerstatsAll.loc[:,'GoalsPer90'] = 90*(playerstatsAll.loc[:,'Goals']/playerstatsAll.loc[:,'Mins'])
    gsDF = playerstatsAll[playerstatsAll['Goals']>=minGoals]    
    
    if 'PointsWon' in pointsaxis:
        maxptsall= datatoplot['PointsWon'].max()
        ylabel = 'Points Won'
    else:
        maxptsall = datatoplot['PointsNorm'].max()    
        ylabel = 'Points Won (Normalised)'
    
    maxgp90all = gsDF['GoalsPer90'].max()
    maxgoalsAll = gsDF['Goals'].max()
    maxGCgoalsAll = gsDF['GCGoals'].max()
    
    maxpts = datatoplot['PointsNorm'].max()    
    maxgp90 = datatoplot['GoalsPer90'].max()
    maxapps = datatoplot['Appearances'].max()
    maxgcPapp = datatoplot['GCgoalsPapp'].max()
    goalScorers = datatoplot

    x_range = np.arange(0,maxgp90+0.1,0.05)
    x_range = x_range.tolist()
    y_range_max = maxptsall*np.ones(len(x_range))
    y_range_max = y_range_max.tolist()
    
    if 'PointsWon' in pointsaxis:
        y_range = [-1,maxptsall+5]
        y_dtick = 5
    else:
        y_range = [-0.1,maxptsall+0.1]
        y_dtick = 0.05
    
    if 'GCgoalsPapp' in gcgoalsaxis:
        maxgcPapp = datatoplot['GCgoalsPapp'].max()
        y_range_gc = [-0.1,maxgcPapp+0.1]
        y_dtick_gc = 0.1
        ylabel_gc = 'Game-Changing Goals per Appearance'
    else:
        maxGCgoals = datatoplot['GCGoals'].max()
        y_range_gc = [-3,maxGCgoals+7]
        y_dtick_gc = 5  
        ylabel_gc = 'Game-Changing Goals'
        
    if 'All Clubs' not in clubselected:        
        fig = px.scatter(goalScorers,x='GoalsPer90',y=pointsaxis,text='Surname',hover_name='Name',
                     size='Goals',size_max=40)        
        fig.update_traces(textposition='middle left')
        fig1 = px.scatter(goalScorers,x='GoalsPer90',y=gcgoalsaxis,text='Surname',hover_name='Name',
                     size='Goals',size_max=40)
        fig1.update_traces(textposition='middle left')
    else:
        fig = px.scatter(goalScorers,x='GoalsPer90',y=pointsaxis,color='Club',hover_name='Name',
                     size='Goals',size_max=40) 
        fig1 = px.scatter(goalScorers,x='GoalsPer90',y=gcgoalsaxis,color='Club',hover_name='Name',
                     size='Goals',size_max=40)
    
    fig.update_layout(xaxis_title='Goals per 90 mins',yaxis_title=ylabel,
                      xaxis=dict(range=[0,maxgp90all+0.1],tickmode='linear',tick0=0,dtick=0.1),
                      yaxis=dict(range=y_range,tickmode='linear',tick0 = 0,dtick=y_dtick))
    fig1.update_layout(xaxis_title='Goals per 90 mins',yaxis_title=ylabel_gc,
                      xaxis=dict(range=[0,maxgp90+0.1],tickmode='linear',tick0=0,dtick=0.1),
                       yaxis=dict(range=y_range_gc,tickmode='linear',tick0 = 0,dtick=y_dtick_gc))
    return fig,fig1,displaystr

@app.callback(
    Output('players-dropdown','options'),
    Output('players-dropdown','value'),
    Output('players-dropdown-2','options'),
    Output('players-dropdown-2','value'),
    Input('min-goal-slider','value'),
    Input('clubname-dropdown','value')
    )
def playerdropdown(minGoals,clubselected):    
    playerstatsAll = pd.read_csv('epl_aggregate_appearances_with_goals_allplayers_2000_2020.csv')
    
    if 'All Clubs' not in clubselected:        
        playerstats = playerstatsAll[playerstatsAll['Club']==clubselected]
    else:
        playerstats = playerstatsAll

    playerstats = playerstats[playerstats['Goals']>=minGoals]
    playerstats = playerstats.sort_values(by='Goals',ascending=False)
    
    playernames = playerstats['Name'].tolist()
    options_ret = [{'label':i, 'value':i} for i in playernames]
    value_ret = playernames[0]
    
    options_ret2 = options_ret
    value_ret2 = value_ret
    return options_ret,value_ret,options_ret2,value_ret2

@app.callback(
    Output('points-goals','columns'),
    Output('points-goals','data'),
    Input('players-dropdown','value'),
    Input('clubname-dropdown','value')
    )
def update_table(playername,clubselected):
    goaleventsDB = pd.read_csv('epl_goalevents_2000_2020.csv')
    if 'All Clubs' not in clubselected:
        playeridx = (goaleventsDB['Player']==playername) & (goaleventsDB['TeamFor']==clubselected)
    else:
        playeridx = (goaleventsDB['Player']==playername)
    playergoals = goaleventsDB[playeridx]
    playergoals.loc[:,'Date'] = pd.to_datetime(playergoals.loc[:,'Date'])
    playergoals.loc[:,'Date'] = playergoals.loc[:,'Date'].dt.strftime('%A, %d. %B %Y')    
    
    coulumnlist = ['Date','Season','TeamFor','TeamAga','Venue','Time','Score','FTScore','PointsWon']
    columnnames = ['Date','Season','For','Against','Venue','Time','Score','Full Time Score','Points Won']
    columns=[{"name": columnnames[i], "id": coulumnlist[i]} for i in range(len(coulumnlist))]
    playergoalsdict = playergoals.to_dict('records')
    return columns,playergoalsdict

@app.callback(
    Output('gc-goals','columns'),
    Output('gc-goals','data'),
    Input('players-dropdown-2','value'),
    Input('clubname-dropdown','value')
    )
def update_table2(playername,clubselected):
    goaleventsDB = pd.read_csv('epl_goalevents_2000_2019.csv')
    if 'All Clubs' not in clubselected:
        playeridx = (goaleventsDB['Player']==playername) & (goaleventsDB['TeamFor']==clubselected)
    else:
        playeridx = (goaleventsDB['Player']==playername)
    playergoals = goaleventsDB[playeridx]
    playergoals.loc[:,'Date'] = pd.to_datetime(playergoals.loc[:,'Date'])
    playergoals.loc[:,'Date'] = playergoals.loc[:,'Date'].dt.strftime('%A, %d. %B %Y')    
    
    gcgoalyes = playergoals['GCGoal']==True
    gcgoalno = playergoals['GCGoal']==False
    playergoals.loc[gcgoalyes,'GCGoal'] = 'Yes'
    playergoals.loc[gcgoalno,'GCGoal'] = 'No'
    
    coulumnlist = ['Date','Season','TeamFor','TeamAga','Venue','Time','Score','FTScore','GCGoal']
    columnnames = ['Date','Season','For','Against','Venue','Time','Score','Full Time Score','Game Changing Goal']
    columns=[{"name": columnnames[i], "id": coulumnlist[i]} for i in range(len(coulumnlist))]
    playergoalsdict = playergoals.to_dict('records')
    return columns,playergoalsdict
if __name__ == '__main__':
    app.run_server(debug=True,port=1234)