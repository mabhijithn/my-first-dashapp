#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 12:55:34 2020

@author: abhijith
"""
import json
import pandas as pd

def getgoalscorers(playerfiles,clubname,minGoals=10):
    '''
    

    Parameters
    ----------
    playerfiles : list
         List of paths to player stat JSON files.
    clubname : string
        Name of club of which to pick goal-scorers.
    minGoals : int, optional
        DESCRIPTION. The default is 10.

    Returns
    -------
    pandas dataframe.
    Containing name, goals, appearance, minutes, game-changing goals and points won for their team

    '''
    goalScorers = pd.DataFrame(columns=['Name','Goals','Appearances','Minutes','GCgoals','Points'])
    for playerfile in playerfiles:
        with open(playerfile,'r') as p:
            player = json.load(p)
        clubStats = player['clubStats']
        idx = next((idx for idx,d in enumerate(clubStats) if clubname in d['club']),None)
        if idx is not None:
            clubStat = clubStats[idx]
            if clubStat['goals']>minGoals:
                goalScorer = {'Name':player['name'],'Goals':clubStat['goals'],
                          'Appearances':clubStat['appearances'],'Minutes':clubStat['minsPlayed'],
                           'GCgoals':clubStat['gcGoal'],'Points':clubStat['pointsWon']
                             }
                goalScorers = goalScorers.append(goalScorer,ignore_index=True)
    return goalScorers