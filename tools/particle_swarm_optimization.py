"""Hace el histograma
summary_
"""
import os

import warnings

import pandas as pd
import numpy as np

import tools.histogram_single_microcircuit as hist_spikes

#from assets.potjans_diesmann.sim_params import sim_dict

warnings.filterwarnings("ignore")

def generate_first_population(folder_path, n_pop, params):
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
        r_params = np.random.random_sample((1,params))/10
        if r_params[0,1] > r_params[0,0]:
            r_params[0,1] = r_params[0,0]
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


def get_subject(folder_path, trial, id_suj, n_params):
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
    params = range(0, n_params)
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


def new_conn_probs_alternative(params):
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
    for j in [0]:
        for i in range(2):
            conn_probs[i, j] = params[cont]
            cont=cont+1

    # cont = 0
    # for j in [4,6]:
    #     for i in [0,1,4,5]:
    #         conn_probs[i, j] = params[cont]
    #         cont=cont+1

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
    params = range(8)
    names = np.concatenate((cols, params), axis=None)

    df = pd.read_csv(os.path.join(folder_path, 'results.csv'), header=None, names=names)

    m = df.columns.to_list()
    performance = df[(df['trials']==trial) & (df['subjects']==id_suj)][m[-1]].values

    try:
        return performance
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
    params = range(8)
    names = np.concatenate((cols, params), axis=None)

    df = pd.read_csv(os.path.join(folder_path, 'results.csv'), header=None, names=names)
    if id_suj == -1:
        result = df[(df['subjects']<=100)].sort_values('7').values
    else:
        result = df[(df['subjects']==id_suj)].sort_values('7').values
    return result


def save_result(folder_path, trial, suj_id, activity):
    """_summary_

    Args:
        folder_path (_type_): _description_
        subject_path (_type_): _description_
        trial (_type_): _description_
        suj_id (_type_): _description_
    """

    performance = perf_calculation(activity)

    print(np.size(activity.tolist()))
    print(np.size(performance))
    df = pd.DataFrame([[trial,suj_id]+activity.tolist()+performance])

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
    df = pd.DataFrame([[trial,suj_id]+list(activity)+[performance]])

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

    activity = np.array(activity)

    # Normalización
    n = (activity[1]-activity[0])/100
    m = activity[0]
    norm_77, norm_24 = 77*n+m, 24*n+m

    return [activity[0], abs(norm_77-activity[2]), abs(norm_24-activity[3]), activity[0] + abs(norm_77-activity[2])+ abs(norm_24-activity[3])]


def modify_performance(folder_path):
    """_summary_

    Args:
        folder_path (_type_): _description_
    """

    # add columns names
    cols = np.array(['trials', 'subjects'])
    params = range(4)
    names = np.concatenate((cols, params), axis=None)

    df = pd.read_csv(os.path.join(folder_path, 'results.csv'), header=None, names=names)
    m = df.columns.to_list()

    trial = df['trials'].unique()
    subject = df['subjects'].unique()

    for trl in trial:
        for suj in subject:

            activity = df[(df['trials']==trl) & (df['subjects']==suj)][m[2:5]].values[0]
            per = perf_calculation(activity)

            n_df = pd.DataFrame([np.concatenate(([trl, suj], activity, per), axis=None)])
            n_df.to_csv(os.path.join(folder_path, 'results_mod.csv'), mode='a', index=False, header=False)


def generate_next_iteration(folder_path, last_trial, n_subjects, params):
    """_summary_

    Args:
        folder_path (_type_): _description_
        last_trial (_type_): _description_
        n_subjects (_type_): _description_
    """

    # Parameters
    w = 0.2
    c1, c2, c3 = 0.3, 0.3, 0.5

    # Get best of all
    best_all_id = sorted_result(folder_path, -1)
    best_all = get_subject(folder_path, best_all_id[0][0], best_all_id[0][1], params)
    

    print('***********************')
    print(best_all_id[0,[0, 1, 9]])
    print('***********************')

    for i in range(n_subjects):

        subject_i = get_subject(folder_path, last_trial, i, params)

        best_subject_i_id = sorted_result(folder_path, i)
        best_subject_i = get_subject(folder_path, best_subject_i_id[0][0], best_subject_i_id[0][1], params)
        print(best_subject_i_id[0,[0, 1, 9]])
        print('***************')

        if last_trial == 0:
            vel = subject_i - subject_i
        else:
            vel = subject_i - get_subject(folder_path, last_trial-1, i, params)

        #r_trial = 1/np.log(last_trial-57)
        rand1 = np.random.random_sample((1,params))
        rand2 = np.random.random_sample((1,params))
        rand3 = np.random.uniform(-0.01,0.01,(1,params))

        new_position = subject_i + w*vel + rand1*c1*(best_subject_i-subject_i) + rand2*c2*(best_all-subject_i) + rand3*c3

        print(subject_i)
        print(w*vel)
        print(rand1*c1*(best_subject_i-subject_i))
        print(rand2*c2*(best_all-subject_i))
        print(rand3*c3)
        #+ np.random.randn()*c3*(rand_subj-subject_i)#*r_trial

        # check negatives
        new_position[new_position<0] = 0

        # check big numbers
        new_position[new_position>0.1] = 0.1
        
        if new_position[0,1] > new_position[0,0]:
            new_position[0,1] = new_position[0,0]

        suj_id = np.array([last_trial+1, i])
        suj = np.concatenate((suj_id, new_position[0]))
        add_suj_to_csv(folder_path, [suj])




