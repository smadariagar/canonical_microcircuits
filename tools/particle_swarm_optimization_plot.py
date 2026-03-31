"""Hace el histograma
summary_
"""
import os

import warnings

import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
import seaborn as sns

import tools.histogram_single_microcircuit as hist_spikes
import tools.particle_swarm_optimization as pso

#from astools/particle_swarm_optimization.pysets.potjans_diesmann.sim_params import sim_dict

warnings.filterwarnings("ignore")

def plot_params(folder_path, trial, subject):
    """_summary_

    Args:
        folder_path (_type_): _description_
        trial (_type_): _description_
        subject (_type_): _description_
    """

    trial, subject = [trial], [subject]

    # add columns names
    cols = np.array(['trials', 'subjects'])
    params = range(8*3)
    names = np.concatenate((cols, params), axis=None)
    df = pd.read_csv(os.path.join(folder_path, 'swarm.csv'), header=None, names=names)

    params = range(5)
    names = np.concatenate((cols, params), axis=None)
    df2 = pd.read_csv(os.path.join(folder_path, 'results.csv'), header=None, names=names)

    if trial[0] == -1:
        trial = df['trials'].unique()
    if subject[0] == -1:
        subject = df['subjects'].unique()
        best_subj = False
    else:
        best_subj = True

    params = df[df['trials'].isin(trial) & df['subjects'].isin(subject)].sort_values('trials', ascending=False).values
    clrs = sns.color_palette('husl', n_colors=20)
    line, lw = '.--', 1

    fig, ax = plt.subplots(3, layout='constrained', figsize=(6,6), sharex=True)
    for i in range(20):
        if len(trial) == 1:
            aux_trl = trial[0]
        else:
            aux_trl = trial[-(i+1)]
        perf = get_result(folder_path, aux_trl, subject[0])[-1]
        ax[0].plot(range(0,8), params[i][2:10], line, lw=lw, c=clrs[i])
        ax[1].plot(range(0,8), params[i][10:18], line, lw=lw, c=clrs[i])
        ax[2].plot(range(0,8), params[i][18:26], line, lw=lw, c=clrs[i],
            label='trl '+str(int(params[i][0]))+
                ', suj '+str(int(params[i][1]))+
                ', perf '+str(round(perf,2)))
    ax[0].set_ylabel('L2/3 E')
    ax[1].set_ylabel('L5 E')
    ax[2].set_ylabel('L6 E')
    ax[2].set_xticks(range(8),['L23E','L23I','L4E','L4I','L5E','L5I','L6E','L6I'])
    if np.size(params, axis=0) <= 10:
        ax[2].legend(loc='lower right')

    if best_subj:
        best_id = sorted_result(folder_path, subject[0])
        best = get_subject(folder_path, best_id[0][0], best_id[0][1])
        ax[0].plot(range(0,8), best[0:8], '.-', lw=1.2, c='r')
        ax[1].plot(range(0,8), best[8:16], '.-', lw=1.2, c='r')
        ax[2].plot(range(0,8), best[16:24], '.-', lw=1.2, c='r',
            label='trl '+str(int(best_id[0][0]))+
                ', suj '+str(int(best_id[0][1]))+
                ', perf '+str(round(best_id[0][2],3)))

    plot_best = True
    if plot_best:
        best_all_id = sorted_result(folder_path, -1)
        best_all = get_subject(folder_path, best_all_id[0][0], best_all_id[0][1])
        ax[0].plot(range(0,8), best_all[0:8], '.-', lw=1, c='k')
        ax[1].plot(range(0,8), best_all[8:16], '.-', lw=1, c='k')
        ax[2].plot(range(0,8), best_all[16:24], '.-', lw=1, c='k',
            label='trl '+str(int(best_all_id[0][0]))+
                ', suj '+str(int(best_all_id[0][1]))+
                ', perf '+str(round(best_all_id[0][2],3)))

    fig.legend(loc='upper left', bbox_to_anchor=(1.0,1),
            fancybox=True, shadow=False, ncol=1)


def plot_best_params(folder_path, type_best):
    """_summary_

    Args:
        folder_path (_type_): _description_
        type_best (_type_): _description_
    """

    clrs = sns.color_palette('coolwarm', n_colors=20)

    if type_best == 'sub':
        fig, ax = plt.subplots(3, layout='constrained', figsize=(6,6), sharex=True)
        for i in range(20):
            best_trial = sorted_result(folder_path, i)
            best_params = get_subject(folder_path, best_trial[0][0], best_trial[0][1])

            ax[0].plot(range(0,8), best_params[0:8], '.--', c=clrs[i])
            ax[1].plot(range(0,8), best_params[8:16], '.--', c=clrs[i])
            ax[2].plot(range(0,8), best_params[16:24], '.--', c=clrs[i],
                label='trl '+str(int(best_trial[0][0]))+
                    ', suj '+str(int(best_trial[0][1]))+
                    ', perf '+str(round(best_trial[0][2],3)))
        ax[0].set_ylabel('L2/3 E')
        ax[1].set_ylabel('L5 E')
        ax[2].set_ylabel('L6 E')
        ax[2].set_xticks(range(8),['L23E','L23I','L4E','L4I','L5E','L5I','L6E','L6I'])
        fig.legend(loc='upper left', bbox_to_anchor=(1.0,1),
            fancybox=True, shadow=False, ncol=1)

    if type_best == 'all':

        fig, ax = plt.subplots(3, layout='constrained', figsize=(6,6), sharex=True)
        best_trial = pso.sorted_result(folder_path, -1)
        group_params = []
        for i in range(20):
            try:
                best_params = pso.get_subject(folder_path, best_trial[i][0], best_trial[i][1], 8)
            except:
                continue
            group_params.append(best_params)
            ax[0].plot(range(0,4), best_params[0:4], '.--', c=clrs[i])
            ax[1].plot(range(0,4), best_params[0:4], '.--', c=clrs[i])
            ax[2].plot(range(0,4), best_params[4:8], '.--', c=clrs[i],
                label='T'+str(int(best_trial[i][0]))+
                    ', S'+str(int(best_trial[i][1]))+
                    '| '+str(round(best_trial[i][3],1))+
                    '| '+str(round(best_trial[i][4],1))+
                    '| '+str(round(best_trial[i][5],1))+'|'+
                    ', perf:'+str(round(best_trial[i][2],1)))
        ax[0].set_ylabel('L2/3 E')
        ax[1].set_ylabel('L5 E')
        ax[2].set_ylabel('L6 E')
        #ax[2].set_xticks(range(8),['L23E','L23I','L4E','L4I','L5E','L5I','L6E','L6I'])
        ax[2].set_xticks(range(4),['L23E','L23I','L5E','L5I'])
        fig.legend(loc='upper left', bbox_to_anchor=(1.0,1),
            fancybox=True, shadow=False, ncol=1)

        #f = open(os.path.join(folder_path, 'test.csv'), "w+", encoding="utf-8")
        #f.close()

        df = pd.DataFrame([np.mean(group_params,axis=0)])
        df.to_csv(os.path.join(folder_path, 'test.csv'), mode='a', index=False, header=False)    
        

        df = pd.DataFrame([np.std(group_params,axis=0)])
        df.to_csv(os.path.join(folder_path, 'test.csv'), mode='a', index=False, header=False)    





def plot_performance(folder_path, trial, subject, trl_plt):
    """_summary_

    Args:
        folder_path (_type_): _description_
        trial (_type_): _description_
        subject (_type_): _description_
        trl_plt (_type_): _description_

    Returns:
        _type_: _description_
    """

    trial, subject, x_adj = [trial], [subject], [0]

    # add columns names
    cols = np.array(['trials', 'subjects'])
    params = range(5)
    names = np.concatenate((cols, params), axis=None)

    df = pd.read_csv(os.path.join(folder_path, 'results.csv'), header=None, names=names)
    m = df.columns.to_list()

    if trial[0] == -1:
        trial = df['trials'].unique()
        clrs = sns.color_palette('husl', n_colors=len(trial))  # a list of RGB tuples
        if trl_plt != -1:
            trial = trial[trl_plt:]

    best_trial = sorted_result(folder_path, -1)[0]
    bottom = best_trial[2]
    if subject[0] == -1:
        subject = df['subjects'].unique()
        x_adj = np.linspace(-0.3,0.3,len(subject))
        clrs = sns.color_palette('husl', n_colors=len(subject))  #len(subject) a list of RGB tuplesv
    else:
        best_trial = sorted_result(folder_path, subject[0])[0]

    #fig = plt.subplots(layout='constrained', figsize=(len(trial)/2+len(subject)/5,4))
    fig = plt.subplots(layout='constrained', figsize=(8,3))
    plt.xlim([np.min(trial)-.5, np.max(trial)+.5])
    plt.xticks(trial[0:-1:5], trial[0:-1:5])
    
    for trl in trial:
        for i, suj in enumerate(subject):
            
            if x_adj[0] != 0:
                col = suj
            else:
                col = trl
            
            perf = df[(df['trials']==trl) & (df['subjects']==suj)][m[6]].values[0]

            if int(trl) == int(best_trial[0]) and int(suj) == int(best_trial[1]):
                plt.scatter(trl+x_adj[i], perf, marker='*', c=clrs[int(col)], 
                    label='trl '+str(int(trl))+
                        ', suj '+str(int(suj))+
                        ', perf '+str(round(perf,2)))
            else:
                plt.scatter(trl+x_adj[i], perf, marker='o', c=clrs[int(col)])
    
    top = plt.ylim()[1]  # return the current ylim
    plt.ylim([bottom*0.5, top*5])
    plt.yscale('log')

    plt.legend(loc='lower right', bbox_to_anchor=(1,1.01),
            fancybox=True, shadow=False, ncol=1)
    plt.grid(visible=True)

def plot_activity(folder_path, trial, subject, trl_plt):
    """_summary_

    Args:
        folder_path (_type_): _description_
        trial (_type_): _description_
        subject (_type_): _description_
        trl_plt (_type_): _description_
    """

    trial, subject, x_adj = [trial], [subject], [0]

    # add columns names
    cols = np.array(['trials', 'subjects'])
    params = range(5)
    names = np.concatenate((cols, params), axis=None)

    df = pd.read_csv(os.path.join(folder_path, 'results.csv'), header=None, names=names)
    m = df.columns.to_list()

    if trial[0] == -1:
        trial = df['trials'].unique()
        trial = trial[trl_plt:]

    if subject[0] == -1:
        subject = df['subjects'].unique()
        x_adj = np.linspace(-0.3,0.3,len(subject))

    # print activity
    fig = plt.subplots(layout='constrained', figsize=(5,4))
    clrs = sns.color_palette('husl', n_colors=10)  # a list of RGB tuples

    for trl in trial:
        for i, suj in enumerate(subject):
            actv = df[(df['trials']==trl) & (df['subjects']==suj)][m[2:6]].values[0]
            for j, sim in enumerate(actv):
                plt.scatter(j+x_adj[i], sim, c=clrs[suj-1])
    #plt.ylim([0,1000])
    #plt.yscale('log')
    plt.xlim([-.5, 3.5])
    plt.xticks(range(4), ['BG','CRF', 'ECRF', 'WTA-ECRF'])


    # print activity
    fig = plt.subplots(layout='constrained', figsize=(5,4))
    clrs = sns.color_palette('husl', n_colors=10)  # a list of RGB tuples

    for i, suj in enumerate(subject):
        actv = df[(df['subjects']==suj)][m[2:6]].values

        mean_actv, std_actv = np.mean(actv, axis=0), np.std(actv, axis=0)
        print(mean_actv)
        print(std_actv)

        for j, sim in enumerate(actv):
            plt.errorbar(range(4)+x_adj[i], mean_actv, 0, ls='', marker='.', ms=8, c=clrs[suj-1])
    #plt.ylim([0,1000])
    #plt.yscale('log')
    plt.xlim([-.5, 3.5])
    plt.xticks(range(4), ['BG','CRF', 'ECRF', 'WTA-ECRF'])


def plot_params_2_var(folder_path, trial, subject, var, n_points):
    """_summary_

    Args:
        folder_path (_type_): _description_
        trial (_type_): _description_
        subject (_type_): _description_
    """

    trial, subject = [trial], [subject]

    # add columns names
    cols = np.array(['trials', 'subjects'])
    params = range(8*3)
    names = np.concatenate((cols, params), axis=None)

    df = pd.read_csv(os.path.join(folder_path, 'swarm.csv'), header=None, names=names)

    if trial[0] == -1:
        trial = df['trials'].unique()
    if subject[0] == -1:
        subject = df['subjects'].unique()
        best_subj = False
    else:
        best_subj = True

    params = df[df['trials'].isin(trial) & df['subjects'].isin(subject)].sort_values('trials', ascending=False).values
    clrs = sns.color_palette('husl', n_colors=n_points)
    line, lw = '.--', 1
    n_points-=1
    fig, ax = plt.subplots(1, layout='constrained', figsize=(4,4), sharex=True)
    for i in range(n_points+1):
        perf = get_result(folder_path, trial[n_points-i], subject[0])[-1]
        ax.scatter(params[n_points-i][var[0]+2], params[n_points-i][var[1]+2], 
            marker='o', c=clrs[i],
            label='trl '+str(int(params[n_points-i][0]))+
                ', suj '+str(int(params[n_points-i][1]))+
                ', perf '+str(round(perf,2)))
    ax.set_xlabel('L2/3 E')
    ax.set_ylabel('L2/3 I')
    if np.size(params, axis=0) <= 10:
        ax.legend(loc='lower right')

    if best_subj:
        best_id = sorted_result(folder_path, subject[0])
        best = get_subject(folder_path, best_id[0][0], best_id[0][1])
        ax.scatter(best[var[0]], best[var[1]], marker='*', c='r',
            label='trl '+str(int(best_id[0][0]))+
                ', suj '+str(int(best_id[0][1]))+
                ', perf '+str(round(best_id[0][2],2)))
    plt.xlim([0, 0.1])
    plt.ylim([0, 0.1])

    plot_best = True
    if plot_best:
        best_all_id = sorted_result(folder_path, -1)
        best_all = get_subject(folder_path, best_all_id[0][0], best_all_id[0][1])
        ax.scatter(best_all[var[0]], best_all[var[1]], marker='*', c='k',
            label='trl '+str(int(best_all_id[0][0]))+
                ', suj '+str(int(best_all_id[0][1]))+
                ', perf '+str(round(best_all_id[0][2],2)))

    fig.legend(loc='upper left', bbox_to_anchor=(1.0,1),
            fancybox=True, shadow=False, ncol=1)


def plot_best_params_32(folder_path, type_best):
    """_summary_

    Args:
        folder_path (_type_): _description_
        type_best (_type_): _description_
    """

    clrs = sns.color_palette('husl', n_colors=20)

    if type_best == 'sub':
        fig, ax = plt.subplots(3, layout='constrained', figsize=(6,6), sharex=True)
        for i in range(20):
            best_trial = sorted_result(folder_path, i)
            best_params = get_subject(folder_path, best_trial[0][0], best_trial[0][1])

            ax[0].plot(range(0,8), best_params[0:8], '.--', c=clrs[i])
            ax[1].plot(range(0,8), best_params[8:16], '.--', c=clrs[i])
            ax[2].plot(range(0,8), best_params[16:24], '.--', c=clrs[i],
                label='trl '+str(int(best_trial[0][0]))+
                    ', suj '+str(int(best_trial[0][1]))+
                    ', perf '+str(round(best_trial[0][2],3)))
        ax[0].set_ylabel('L2/3 E')
        ax[1].set_ylabel('L5 E')
        ax[2].set_ylabel('L6 E')
        ax[2].set_xticks(range(8),['L23E','L23I','L4E','L4I','L5E','L5I','L6E','L6I'])
        fig.legend(loc='upper left', bbox_to_anchor=(1.0,1),
            fancybox=True, shadow=False, ncol=1)

    if type_best == 'all':
        fig, ax = plt.subplots(4, layout='constrained', figsize=(6,6), sharex=True, sharey=True)
        best_trial = sorted_result(folder_path, -1)
        print(best_trial)
        group_params = []
        for i in range(20):
            best_params = get_subject(folder_path, best_trial[i][0], best_trial[i][1])
            print(best_params)
            group_params.append(best_params)
            ax[0].plot(range(0,8), best_params[0:8], '.--', c=clrs[i])
            ax[1].plot(range(0,8), best_params[8:16], '.--', c=clrs[i])
            ax[2].plot(range(0,8), best_params[16:24], '.--', c=clrs[i])
            ax[3].plot(range(0,8), best_params[24:32], '.--', c=clrs[i],
                label='trl '+str(int(best_trial[i][0]))+
                    ', suj '+str(int(best_trial[i][1]))+
                    ', perf '+str(round(best_trial[i][2],3)))
        ax[0].set_ylabel('L2/3 E')
        ax[1].set_ylabel('L5 E')
        ax[2].set_ylabel('L6 E')
        ax[3].set_ylabel('Th B')
        ax[3].set_xticks(range(8),['L23E','L23I','L4E','L4I','L5E','L5I','L6E','L6I'])
        fig.legend(loc='upper left', bbox_to_anchor=(1.0,1),
            fancybox=True, shadow=False, ncol=1)

        df = pd.DataFrame([np.mean(group_params,axis=0)])
        df.to_csv(os.path.join(folder_path, 'test.csv'), mode='a', index=False, header=False)    
        

        df = pd.DataFrame([np.std(group_params,axis=0)])
        df.to_csv(os.path.join(folder_path, 'test.csv'), mode='a', index=False, header=False)    

