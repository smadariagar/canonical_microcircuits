"""Hace el histograma
summary_
"""
import os

import json
import warnings
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt
from itertools import combinations

from utils.helpers import __load_meter_data
import tools.histogram_single_microcircuit as hist_spikes

#from assets.potjans_diesmann.sim_params import sim_dict

warnings.filterwarnings("ignore")

def generate_first_generation(folder_path, n_ind):

    # opening the file with w+ mode truncates the file
    f = open(os.path.join(folder_path, 'generations.csv'), "w+")
    f.close() 

    # opening the file with w+ mode truncates the file
    f = open(os.path.join(folder_path, 'performance.csv'), "w+")
    f.close()  

    for i in range(n_ind):
        suj_id = np.array([[0, i]])
        r_params = np.random.random_sample((1,8*3))/10
        suj = np.concatenate((suj_id, r_params), axis=1)

        add_suj_to_csv(folder_path, suj)


def add_suj_to_csv(folder_path, suj_info):
    
    # convert array into dataframe 
    df = pd.DataFrame(suj_info) 
    
    # save the dataframe as a csv file 
    # append data frame to CSV file
    df.to_csv(os.path.join(folder_path, 'generations.csv'), mode='a', index=False, header=False)


def get_subject(folder_path, gen, id_suj):
    
    # add columns names
    cols = np.array(['generation', 'subject'])
    params = range(0, 8*3)
    names = np.concatenate((cols, params), axis=None)
    
    df = pd.read_csv(os.path.join(folder_path, 'generations.csv'), header=None, names=names)

    m = df.columns.to_list()
    suj_params = df[(df['generation']==gen) & (df['subject']==id_suj)][m[2:]].values.tolist()

    return suj_params[0]

def get_best_subject(folder_path, gen, id_suj):
    
    # add columns names
    df = pd.read_csv(os.path.join(folder_path, 'best_generations.csv'), header=None, names=None)

    suj_params = df.values[gen,:].tolist()

    return suj_params


def new_conn_probs(params):

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


def save_performance(folder_path, subject_path, suj_id):

    data, bins = hist_spikes.apliccation_metrics(subject_path)
    L23E = data[1]
    
    perf = [np.mean(L23E[1:25]), np.mean(L23E[25:50]), np.mean(L23E[50:75]), np.mean(L23E[75:100])]

    # convert array into dataframe 
    df = pd.DataFrame([suj_id+perf]) 
    
    # save the dataframe as a csv file 
    # append data frame to CSV file
    df.to_csv(os.path.join(folder_path, 'performance.csv'), mode='a', index=False, header=False)


def generate_next_generation(folder_path, last_generation):

    # add columns names
    cols = np.array(['generation', 'subject'])
    params = range(4)
    names = np.concatenate((cols, params), axis=None)
    
    df = pd.read_csv(os.path.join(folder_path, 'performance.csv'), header=None, names=names)
    m = df.columns.to_list()

    perf_last_gen = []
    for i in range(10):
        perf = df[(df['generation']==last_generation) & (df['subject']==i)][m[2:]].values.tolist()
        perf_last_gen.append(perf_calculation(perf[0]))
    perf_last_gen_sorted = sorted(range(len(perf_last_gen)), key=lambda k: perf_last_gen[k])
    
    comb = combinations(perf_last_gen_sorted[0:5], 2)
    new_suj = 0
    for parents in list(comb):
        new_param_suj = making_babies(folder_path, last_generation, parents[0], parents[1])

        suj_id = np.array([last_generation+1, new_suj])
        suj = np.concatenate((suj_id, new_param_suj))

        add_suj_to_csv(folder_path, [suj])
        new_suj = new_suj+1


def perf_calculation(perf):

    ###################################
    # MCC conn_prob_lat = 0           #
    # Basal= 86 +- 26; CRF= 110 +- 24 #
    ###################################
    perf = np.array(perf)
    
    #ext_val = abs(86-perf[0])
    ext_val = 0

    supp_val = 0
    if perf[1] < perf[2]:
        supp_val = abs(perf[2]-perf[1])
        if perf[2] < perf[3]:
            supp_val = supp_val+abs(perf[3]-perf[2])
     
    n = 100/(perf[1]-perf[0])
    m = -n*perf[0]
    norm_perf = perf*n+m

    return ext_val+supp_val+abs(80-norm_perf[2])+abs(20-norm_perf[3])

def making_babies(folder_path, generation, parent0_id, parent1_id):
    
    parent0 = get_subject(folder_path, generation, parent0_id)
    parent1 = get_subject(folder_path, generation, parent1_id)

    baby = []
    for gen in range(len(parent0)):
        if np.random.random_sample() >= 0.5:
            baby.append(parent0[gen])
        else:
            baby.append(parent1[gen])

        if np.random.random_sample() >= 0.5:
            baby[gen] = baby[gen] + (np.random.randn()/50)

        if baby[gen] < 0:
            baby[gen] = 0
        
    return np.array(baby)


def sort_best_performance(folder_path):
    
    # add columns names
    cols = np.array(['generation', 'subject'])
    params = range(0, 8)
    names = np.concatenate((cols, params), axis=None)
    
    df = pd.read_csv(os.path.join(folder_path, 'performance.csv'), header=None, names=names)
    m = df.columns.to_list()

    perf_all = []
    for i in range(np.size(df['1'])):
        perf = df.values[i,2:].tolist()
        perf_all.append(perf_calculation(perf))
    perf_all = sorted(range(len(perf_all)), key=lambda k: perf_all[k])
    
    all_best_params = []
    for best in range(10):
        best_suj = df.values[perf_all[best],:2].tolist()
        par = get_subject(folder_path, best_suj[0], best_suj[1])
        all_best_params.append(par)

        # convert array into dataframe 
        dfn = pd.DataFrame([par]) 
    
        # save the dataframe as a csv file 
        # append data frame to CSV file
        dfn.to_csv(os.path.join(folder_path, 'best_generations.csv'), mode='a', index=False, header=False)
        
    plot_params(all_best_params)


def plot_params(params):
    
    print(np.mean(params, axis=0))
    print(np.std(params, axis=0))


    fig = plt.figure()
    for i in range(np.size(params, axis=0)):
        plt.plot(range(24),params[:][i], '.--')


    fig2 = plt.figure()
    plt.errorbar(range(24), np.mean(params, axis=0), np.std(params, axis=0))

    plt.show()

    