#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Dec  2 12:52:26 2020

@author: abhijith
"""
from app import app
from app import server
import dash_html_components as html
import dash_core_components as dcc
import json
import plotly.express as px
import pandas as pd

LFC_gScorers = pd.read_csv('LFC_gScorers.csv')
goalScorers = LFC_gScorers
goalScorers.sort_values(by='Goals',ascending=False,inplace=True)
goalScorers['Goals'] = pd.to_numeric(goalScorers['Goals'])
goalScorers['GCgoals'] = pd.to_numeric(goalScorers['GCgoals'])
goalScorers['Appearances'] = pd.to_numeric(goalScorers['Appearances'])
goalScorers['Minutes'] = pd.to_numeric(goalScorers['Minutes'])
goalScorers.loc[:,'GoalsPer90'] = 90*(goalScorers.loc[:,'Goals']/goalScorers.loc[:,'Minutes'])
goalScorers.loc[:,'PointsNorm'] = goalScorers.loc[:,'Points']/(3*goalScorers.loc[:,'Appearances'])
    
fig = px.scatter(goalScorers,x='GoalsPer90',y='PointsNorm',color='Name',
                 size='Goals',size_max=40)
fig.update_layout(xaxis_title='Goals per 90 mins',yaxis_title='Points won for team (normalised)')


app.layout = html.Div(children=[
    html.H1(children='Liverpool: Goal scorers of 21st century'),

    html.Div(children='''
        Visualization to contrast `Impact' of goal scorers. The data used is premier league goals from 2000-2001 season to 2019-2020
    '''),

    dcc.Graph(
        id='gper90-v-ptsnorm-graph',
        figure=fig
    )
])
             
if __name__ == '__main__':
    app.run_server(debug=True)