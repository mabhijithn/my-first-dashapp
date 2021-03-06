#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec  4 12:55:34 2020

@author: abhijith
"""
import json
import pandas as pd

def getgoalscorers(playerfiles,clubname):
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
    
    goalScorers = pd.DataFrame(columns=['Name','ID','Club','Goals','Appearances','Minutes','GCgoals','Points'])
    for playerfile in playerfiles:
        with open(playerfile,'r') as p:
            player = json.load(p)
        clubStats = player['clubStats']
        if 'All Clubs' in clubname:
            for clubStat in clubStats:
                if 'appearances' in clubStat:
                    if clubStat['goals']>0:
                        goalScorer = {'Name':player['name'],'ID':player['id'],'Club':clubStat['club'],'Goals':clubStat['goals'],
                                  'Appearances':clubStat['appearances'],'Minutes':clubStat['minsPlayed'],
                                   'GCgoals':clubStat['gcGoal'],'Points':clubStat['pointsWon']
                                     }
                        goalScorers = goalScorers.append(goalScorer,ignore_index=True)
        else:
            idx = next((idx for idx,d in enumerate(clubStats) if clubname in d['club']),None)
            if idx is not None:
                clubStat = clubStats[idx]
                if 'appearances' in clubStat:
                    if clubStat['goals']>0:
                        goalScorer = {'Name':player['name'],'Club':clubStat['club'],'Goals':clubStat['goals'],
                                  'Appearances':clubStat['appearances'],'Minutes':clubStat['minsPlayed'],
                                   'GCgoals':clubStat['gcGoal'],'Points':clubStat['pointsWon']
                                     }
                        goalScorers = goalScorers.append(goalScorer,ignore_index=True)
    maxGoals = goalScorers['Goals'].max()
        
    return goalScorers,maxGoals