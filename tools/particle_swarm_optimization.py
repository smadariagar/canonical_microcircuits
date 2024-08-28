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

#from assets.potjans_diesmann.sim_params import sim_dict

warnings.filterwarnings("ignore")

def generate_first_population(folder_path, n_pop):
    """_summary_

    Args:
        folder_path (_type_): _description_
        n_pop (_type_): _description_
    """

    # opening the file with w+ mode truncates the file
    f = open(os.path.join(folder_path, 'swarm.csv'), "w+", encoding="utf-8")
    f.close()

    # opening the file with w+ mode truncates the file
    f = open(os.path.join(folder_path, 'results.csv'), "w+", encoding="utf-8")
    f.close()

    for i in range(n_pop):
        suj_id = np.array([[0, i]])
        r_params = np.random.random_sample((1,8*3))/10
        suj = np.concatenate((suj_id, r_params), axis=1)

        add_suj_to_csv(folder_path, suj)


def add_suj_to_csv(folder_path, suj_info):
    """_summary_

    Args:
        folder_path (_type_): _description_
        suj_info (_type_): _description_
    """

    # convert array into dataframe
    df = pd.DataFrame(suj_info)

    # save the dataframe as a csv file
    # append data frame to CSV file
    df.to_csv(os.path.join(folder_path, 'swarm.csv'), mode='a', index=False, header=False)


def get_subject(folder_path, trial, id_suj):
    """_summary_

    Args:
        folder_path (_type_): _description_
        trial (_type_): _description_
        id_suj (_type_): _description_

    Returns:
        _type_: _description_
    """

    # add columns names
    cols = np.array(['trials', 'subjects'])
    params = range(0, 8*3)
    names = np.concatenate((cols, params), axis=None)

    df = pd.read_csv(os.path.join(folder_path, 'swarm.csv'), header=None, names=names)
    m = df.columns.to_list()
    suj_params = df[(df['trials']==trial) & (df['subjects']==id_suj)][m[2:]].values

    try:
        return suj_params[0]
    except Exception:
        return []


def new_conn_probs(params):
    """_summary_

    Args:
        params (_type_): _description_

    Returns:
        _type_: _description_
    """

    conn_probs = np.array(
        [[0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]])
        # L2E  L2I  L4E  L4I  L5E  L5I  L6E  L6I

    cont = 0
    for j in [0,4,6]:
        for i in range(8):
            conn_probs[i, j] = params[cont]
            cont=cont+1

    return conn_probs


def get_result(folder_path, trial, id_suj):
    """_summary_

    Args:
        folder_path (_type_): _description_
        trial (_type_): _description_
        id_suj (_type_): _description_

    Returns:
        _type_: _description_
    """

    # add columns names
    cols = np.array(['trials', 'subjects'])
    params = range(5)
    names = np.concatenate((cols, params), axis=None)

    df = pd.read_csv(os.path.join(folder_path, 'results.csv'), header=None, names=names)

    m = df.columns.to_list()
    performance = df[(df['trials']==trial) & (df['subjects']==id_suj)][m[2:]].values

    try:
        return performance[0]
    except Exception:
        return []


def sorted_result(folder_path, id_suj):
    """_summary_

    Args:
        folder_path (_type_): _description_
        id_suj (_type_): _description_

    Returns:
        _type_: _description_
    """

    # add columns names
    cols = np.array(['trials', 'subjects'])
    params = range(5)
    names = np.concatenate((cols, params), axis=None)

    df = pd.read_csv(os.path.join(folder_path, 'results.csv'), header=None, names=names)
    if id_suj == -1:
        result = df[(df['subjects']<=100)][['trials', 'subjects', '4']].sort_values('4').values
    else:
        result = df[(df['subjects']==id_suj)][['trials', 'subjects', '4']].sort_values('4').values

    return result


def save_result(folder_path, subject_path, trial, suj_id):
    """_summary_

    Args:
        folder_path (_type_): _description_
        subject_path (_type_): _description_
        trial (_type_): _description_
        suj_id (_type_): _description_
    """

    data = hist_spikes.apliccation_metrics(subject_path, 250)[0]
    activity = data[1]

    performance = perf_calculation(activity)

    # convert array into dataframe
    df = pd.DataFrame([[trial,suj_id]+activity+[performance]])

    # save the dataframe as a csv file
    # append data frame to CSV file
    df.to_csv(os.path.join(folder_path, 'results.csv'), mode='a', index=False, header=False)


def save_imposed_result(folder_path, trial, suj_id, activity):
    """_summary_

    Args:
        folder_path (_type_): _description_
        trial (_type_): _description_
        suj_id (_type_): _description_
        activity (_type_): _description_
    """

    performance = perf_calculation(activity)

    # convert array into dataframe
    df = pd.DataFrame([[trial,suj_id]+activity+[performance]])

    # save the dataframe as a csv file
    # append data frame to CSV file
    df.to_csv(os.path.join(folder_path, 'results.csv'), mode='a', index=False, header=False)


def perf_calculation(activity):
    """_summary_

    Args:
        activity (_type_): _description_

    Returns:
        _type_: _description_
    """

    ###################################
    # MCC conn_prob_lat = 0           #
    # Basal= 86 +- 26; CRF= 110 +- 24 #
    # 230.8 370.3 417.2 400.9        #
    ###################################
    activity = np.array(activity)

    # Variable de actividad basal
    bg_val = abs(300-activity[0])
    bg_val = bg_val + abs(430-activity[1])

    # Norm activity to target values
    n = 130/(activity[1]-activity[0])
    m = 300-n*activity[0]
    activity = activity*n+m

    # Variable de supresión
    supp_val = 0
    if activity[1] < activity[2]:
        supp_val = supp_val + abs(activity[2]-activity[1])
    if activity[2] < activity[3]:
        supp_val = supp_val + abs(activity[3]-activity[2])
    if activity[1] < activity[3]:
        supp_val = supp_val + abs(activity[3]-activity[1])

    # Normalización
    n = (activity[1]-activity[0])/100
    m = 299
    norm_77, norm_24 = 77*n+m, 24*n+m

    # Variable supresión inicial
    norm_val_1 = abs(norm_77-activity[2])

    # Variable supresión inicial
    norm_val_2 = abs(norm_24-activity[3])

    if activity[0]==0 and activity[1]==0 and activity[2]==0 and activity[3]==0:
        return 10000000

    return bg_val + supp_val + norm_val_1 + norm_val_2


def modify_performance(folder_path):
    """_summary_

    Args:
        folder_path (_type_): _description_
    """

    # add columns names
    cols = np.array(['trials', 'subjects'])
    params = range(5)
    names = np.concatenate((cols, params), axis=None)

    df = pd.read_csv(os.path.join(folder_path, 'results.csv'), header=None, names=names)
    m = df.columns.to_list()

    trial = df['trials'].unique()
    subject = df['subjects'].unique()

    for trl in trial:
        for suj in subject:

            activity = df[(df['trials']==trl) & (df['subjects']==suj)][m[2:6]].values[0]
            per = perf_calculation(activity)

            n_df = pd.DataFrame([np.concatenate(([trl, suj], activity, per), axis=None)])
            n_df.to_csv(os.path.join(folder_path, 'results_mod.csv'), mode='a', index=False, header=False)


def generate_next_iteration(folder_path, last_trial, n_subjects):
    """_summary_

    Args:
        folder_path (_type_): _description_
        last_trial (_type_): _description_
        n_subjects (_type_): _description_
    """

    # Parameters
    w = 0.2
    c1, c2, c3 = 0.3, 0.3, 1

    # Get best of all
    best_all_id = sorted_result(folder_path, -1)
    best_all = get_subject(folder_path, best_all_id[0][0], best_all_id[0][1])

    print('***********************')
    print(best_all_id[0])
    print('***********************')

    for i in range(n_subjects):

        subject_i = get_subject(folder_path, last_trial, i)

        best_subject_i_id = sorted_result(folder_path, i)
        best_subject_i = get_subject(folder_path, best_subject_i_id[0][0], best_subject_i_id[0][1])
        print(best_subject_i_id[0])
        print('***************')

        if last_trial == 0:
            vel = subject_i - subject_i
        else:
            vel = subject_i - get_subject(folder_path, last_trial-1, i)

        #r_trial = 1/np.log(last_trial-57)
        rand1 = np.random.random_sample((1,8*3))
        rand2 = np.random.random_sample((1,8*3))
        rand3 = np.random.uniform(-0.01,0.01,(1,8*3))

        new_position = subject_i + w*vel + rand1*c1*(best_subject_i-subject_i) + rand2*c2*(best_all-subject_i) + rand3*c3
        #+ np.random.randn()*c3*(rand_subj-subject_i)#*r_trial

        # check negatives
        new_position[new_position<0] = 0

        # check big numbers
        new_position[new_position>0.1] = 0.1

        suj_id = np.array([last_trial+1, i])
        suj = np.concatenate((suj_id, new_position[0]))

        add_suj_to_csv(folder_path, [suj])


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
        perf = get_result(folder_path, trial[0], i)[-1]
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
        ax[0].plot(range(0,8), best[0:8], '.-', lw=1.2, c='m')
        ax[1].plot(range(0,8), best[8:16], '.-', lw=1.2, c='m')
        ax[2].plot(range(0,8), best[16:24], '.-', lw=1.2, c='m',
            label='trl '+str(int(best_id[0][0]))+
                ', suj '+str(int(best_id[0][1]))+
                ', perf '+str(round(best_id[0][2],2)))

    plot_best = True
    if plot_best:
        best_all_id = sorted_result(folder_path, -1)
        best_all = get_subject(folder_path, best_all_id[0][0], best_all_id[0][1])
        ax[0].plot(range(0,8), best_all[0:8], '.-', lw=1, c='k')
        ax[1].plot(range(0,8), best_all[8:16], '.-', lw=1, c='k')
        ax[2].plot(range(0,8), best_all[16:24], '.-', lw=1, c='k',
            label='trl '+str(int(best_all_id[0][0]))+
                ', suj '+str(int(best_all_id[0][1]))+
                ', perf '+str(round(best_all_id[0][2],2)))

    fig.legend(loc='upper left', bbox_to_anchor=(1.0,1),
            fancybox=True, shadow=False, ncol=1)


def plot_best_params(folder_path, type_best):
    """_summary_

    Args:
        folder_path (_type_): _description_
        type_best (_type_): _description_
    """

    clrs = sns.color_palette('husl', n_colors=20)

    if type_best == 'sub':
        fig, ax = plt.subplots(3, layout='constrained', figsize=(6,8), sharex=True)
        for i in range(20):
            best_trial = sorted_result(folder_path, i)
            best_params = get_subject(folder_path, best_trial[0][0], best_trial[0][1])

            ax[0].plot(range(0,8), best_params[0:8], '.--', c=clrs[i])
            ax[1].plot(range(0,8), best_params[8:16], '.--', c=clrs[i])
            ax[2].plot(range(0,8), best_params[16:24], '.--', c=clrs[i],
                label='trl '+str(int(best_trial[0][0]))+
                    ', suj '+str(int(best_trial[0][1]))+
                    ', perf '+str(round(best_trial[0][2],2)))
        ax[0].set_ylabel('L2/3 E')
        ax[1].set_ylabel('L5 E')
        ax[2].set_ylabel('L6 E')
        ax[2].set_xticks(range(8),['L23E','L23I','L4E','L4I','L5E','L5I','L6E','L6I'])
        fig.legend(loc='upper left', bbox_to_anchor=(1.0,1),
            fancybox=True, shadow=False, ncol=1)

    if type_best == 'all':
        fig, ax = plt.subplots(3, layout='constrained', figsize=(6,8), sharex=True)
        best_trial = sorted_result(folder_path, -1)
        for i in range(20):
            best_params = get_subject(folder_path, best_trial[i][0], best_trial[i][1])

            ax[0].plot(range(0,8), best_params[0:8], '.--', c=clrs[i])
            ax[1].plot(range(0,8), best_params[8:16], '.--', c=clrs[i])
            ax[2].plot(range(0,8), best_params[16:24], '.--', c=clrs[i],
                label='trl '+str(int(best_trial[i][0]))+
                    ', suj '+str(int(best_trial[i][1]))+
                    ', perf '+str(round(best_trial[i][2],2)))
        ax[1].set_ylabel('L5 E')
        ax[2].set_ylabel('L6 E')
        ax[2].set_xticks(range(8),['L23E','L23I','L4E','L4I','L5E','L5I','L6E','L6I'])
        fig.legend(loc='upper left', bbox_to_anchor=(1.0,1),
            fancybox=True, shadow=False, ncol=1)


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

    if subject[0] == -1:
        subject = df['subjects'].unique()
        x_adj = np.linspace(-0.3,0.3,len(subject))
        clrs = sns.color_palette('husl', n_colors=10)  # a list of RGB tuplesv
        best_trial = sorted_result(folder_path, -1)[0]
    else:
        best_trial = sorted_result(folder_path, subject[0])[0]

    #fig = plt.subplots(layout='constrained', figsize=(len(trial)/2+len(subject)/5,4))
    fig = plt.subplots(layout='constrained', figsize=(8,3))

    for trl in trial:
        for i, suj in enumerate(subject):
            if x_adj[0] != 0:
                col = suj
            else:
                col = trl

            perf = df[(df['trials']==trl) & (df['subjects']==suj)][m[6]].values[0]

            if int(trl) == int(best_trial[0]) and int(suj) == int(best_trial[1]):
                plt.scatter(trl+x_adj[i], perf, marker='*', c=clrs[int(col)], label='best suj '+str(suj)+' = '+str(perf))
            else:
                plt.scatter(trl+x_adj[i], perf, marker='o', c=clrs[int(col)])

    #plt.yscale('log')
    bottom, top = plt.ylim()  # return the current ylim
    plt.ylim([0, 2500])
    plt.xlim([np.min(trial)-.5, np.max(trial)+.5])
    plt.xticks(trial[0:-1:5], trial[0:-1:5])
    plt.legend(loc='upper right')


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
