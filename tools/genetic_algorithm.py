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


def save_performance(folder_path, suj_info):
    
    # convert array into dataframe 
    df = pd.DataFrame([suj_info]) 
    
    # save the dataframe as a csv file 
    # append data frame to CSV file
    print(folder_path)
    df.to_csv(os.path.join(folder_path, 'performance.csv'), mode='a', index=False, header=False)


def generate_next_generation(folder_path, last_generation):

    # add columns names
    cols = np.array(['generation', 'subject'])
    params = range(0, 8)
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
    
    ext_val = abs(86-perf[0])

    n = 100/(perf[2]-perf[0])
    m = -n*perf[0]

    supp_val = 0
    if perf[2] < perf[4]:
        supp_val = 1
        if perf[4] < perf[6]:
            supp_val = 2
     
    n = 100/(perf[2]-perf[0])
    m = -n*perf[0]
    norm_perf = perf*n+m
    
    #if perf[0]>500:
        #return 1000

    return ext_val+100*supp_val+abs(80-norm_perf[4])+abs(20-norm_perf[6])

def making_babies(folder_path, generation, parent0_id, parent1_id):
    
    parent0 = get_subject(folder_path, generation, parent0_id)
    parent1 = get_subject(folder_path, generation, parent1_id)

    baby = []
    for gen in range(len(parent0)):
        if np.random.random_sample() >= 0.5:
            baby.append(parent0[gen])
        else:
            baby.append(parent1[gen])

        baby[gen] = baby[gen] + (np.random.random_sample()-0.5)/50

        if baby[gen] < 0:
            baby[gen] = 0
        
    return np.array(baby)