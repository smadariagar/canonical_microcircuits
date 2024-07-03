"""Hace el histograma
summary_
"""
import os

import json
import warnings
import pandas as pd
import numpy as np

import matplotlib.pyplot as plt

from utils.helpers import __load_meter_data
#from assets.potjans_diesmann.sim_params import sim_dict

warnings.filterwarnings("ignore")

def generate_first_generation(folder_path, n_ind):

    for i in range(n_ind):
        suj_id = np.array([[0, i]])
        r_params = np.random.random_sample((1,8*3))/5
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

    aux = df[(df['subject']==3) & (df['generation']==0)][m[2:]]

    print(aux)


def apliccation_metrics(folder_path):
    """_summary_

    Args:
        folder_path (_type_): _description_
    """
    # Llama a la función para obtener los archivos que comienzan con "spike_recorder"
    archivos_spike_recorder = select_spike_recorder_files(folder_path)
    info_total, times = process_files_in_pairs_positions(folder_path, archivos_spike_recorder)

    # Mapear las capas a los nuevos nombres
    layer_mapping = {1: '2/3', 2: '4', 3: '5', 4: '6'}
    info_total['Layer'] = info_total['Layer'].map(layer_mapping)

    # Crear un histograma por cada combinación de type y Layer
    unique_combinations = info_total[['type', 'Layer']].drop_duplicates()

    # Configurar el diseño de plots
    fs = 16  # fontsize

    data = []
    # Iterar sobre cada combinación única
    for i, row in enumerate(unique_combinations.itertuples(), 1):
        if i == 9:
            break

        # Crea plots
        fig = plt.figure(figsize=(6, 4))

        subset = info_total[(info_total['type'] == row.type) & (info_total['Layer'] == row.Layer)]

        # Asignar colores según el tipo
        color = '#0063B2' if row.type == 'exc' else '#b015b6'

        # Crear el histograma en la subfigura actual con colores personalizados
        l_bin = 20
        n, bins, rects = plt.hist(
            subset['time'], bins=range(0, int(sim_dict["t_sim"])+l_bin, l_bin), label=f"{row.type}, Layer{row.Layer}",
            color=color, edgecolor='black', linewidth=1.2)

        data.append(n.tolist())

        # Configurar etiquetas y título
        plt.xlabel('time [ms]', fontsize=fs)
        plt.xticks(fontsize=fs)
        plt.ylabel('frequency', fontsize=fs)
        plt.yticks(fontsize=fs)
        plt.title(f'Histogram - {row.type}, Layer {row.Layer}', fontsize=22)
        #ax.set_ylim([0.0, 1500.0])20240405025743
        plt.legend()

        # Ajustar el espaciado entre subplots para evitar superposiciones
        plt.tight_layout()

        # Guardar la figura en un archivo
        plt.savefig(folder_path + "/" + str(i) + "spike_time_histogram.png", dpi=300)


def apliccation_metrics_folders(path, folder):
    """_summary_

    Args:
        folder_path (_type_): _description_
    """
    folder_path = os.path.join(path, folder)

    # Llama a la función para obtener los archivos que comienzan con "spike_recorder"
    archivos_spike_recorder = select_spike_recorder_files(folder_path)
    info_total, times = process_files_in_pairs_positions(folder_path, archivos_spike_recorder)

    # Read JSON
    with open(os.path.join(folder_path, 'sim_params.json'), 'r') as file:
        sim_dict = json.load(file)

    # Mapear las capas a los nuevos nombres
    layer_mapping = {
        1: '2/3a', 2: '4a', 3: '5a', 4: '6a',
        5: '2/3b', 6: '4b', 7: '5b', 8: '6b',
        9: '2/3c', 10: '4c', 11: '5c', 12: '6c',
        13: '2/3d', 14: '4d', 15: '5d', 16: '6d',
    }
    info_total['Layer'] = info_total['Layer'].map(layer_mapping)

    # Crear un histograma por cada combinación de type y Layer
    unique_combinations = info_total[['type', 'Layer']].drop_duplicates()

    # Configurar el diseño de plots
    fs = 16  # fontsize

    data = []
    # Iterar sobre cada combinación única
    for i, row in enumerate(unique_combinations.itertuples(), 1):
        #if i == 9:
            #break
        # Crea plots
        #fig = plt.figure(figsize=(6, 4))

        subset = info_total[(info_total['type'] == row.type) & (info_total['Layer'] == row.Layer)]

        # Asignar colores según el tipo
        color = '#0063B2' if row.type == 'exc' else '#b015b6'

        # Crear el histograma en la subfigura actual con colores personalizados
        l_bin = 20
        n, bins, rects = plt.hist(
            subset['time'], bins=range(0, int(sim_dict["t_sim"])+l_bin, l_bin), label=f"{row.type}, Layer{row.Layer}",
            color=color, edgecolor='black', linewidth=1.2)

        data.append(n.tolist())

        # Configurar etiquetas y título
        #plt.xlabel('time [ms]', fontsize=fs)
        #plt.xticks(fontsize=fs)
        #plt.ylabel('frequency', fontsize=fs)
        #plt.yticks(fontsize=fs)
        #plt.title(f'Histogram - {row.type}, Layer {row.Layer}', fontsize=22)
        #ax.set_ylim([0.0, 1500.0])20240405025743
        #plt.legend()

        # Ajustar el espaciado entre subplots para evitar superposiciones
        #plt.tight_layout()

        # Guardar la figura en un archivo
        #plt.savefig(folder_path + "/" + str(i) + "spike_time_histogram.png", dpi=300)

    return data, bins[0:-1]

# data directory
#id_result = '20240430191512' # Modelo de un microcircuito
#path_result = 'results/potjans_diesmann/'+id_result+'/'

# Llama a la función para obtener los archivos que comienzan con "spike_recorder"
#archivos_spike_recorder = select_spike_recorder_files(path_result)
#apliccation_metrics(path_result, archivos_spike_recorder)
