
from utils.helpers import __load_meter_data
import os
import json
import random
import math
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt
from scipy.fft import fft
warnings.filterwarnings("ignore")



def select_spike_recorder_files(path):
    """
    Select files starting with 'spike_recorder' from the given path.

    Args:
        path (str): The path to the directory.

    Returns:
        list: A list of file names starting with 'spike_recorder'.
    """
    file_names = os.listdir(path)
    spike_recorder_files = [file for file in file_names if file.startswith('spike_recorder')]
    return spike_recorder_files

def extract_time_info(file_path):
    """
    Extract 't_presim' and 't_sim' values from a JSON file.

    Args:
        file_path (str): Path to the JSON file.

    Returns:
        tuple: A tuple containing the 't_presim' and 't_sim' values.
    """
    try:
        with open(file_path, 'r') as file:
            data = json.load(file)
        t_presim = data.get("t_presim")
        t_sim = data.get("t_sim")
        return t_presim, t_sim
    except FileNotFoundError:
        print(f"File not found at the specified path: {file_path}")
        return None, None
    



def process_files_in_pairs_positions(folder_path, spike_recorder_files):
    """
    Process files in pairs and perform operations using extracted information.

    Args:
        folder_path (str): The path to the folder.
        spike_recorder_files (list): List of spike recorder file names.
    """
    if len(spike_recorder_files) % 2 != 0:
        print("Number of files is not even.")
        return
    

    info = []
    times_simulation = []
    for n,i in enumerate(range(0,  len(spike_recorder_files), 2)):
        
        # Lectura de parámetros de simulacion
        file1 = spike_recorder_files[i]
        file2 = spike_recorder_files[i + 1]
        
        t_presim_value, t_sim_value = extract_time_info(folder_path + 'sim_params.json')
        t_presim_value = 0
        times_simulation.append([t_presim_value, t_sim_value])

        # Lectura excitatoria
        exc = __load_meter_data(folder_path, file1, t_presim_value, t_sim_value + t_presim_value)
        cellids, times = zip(*exc[2][0])
        exc_cells = pd.DataFrame({'cellid': cellids, 'time': times})
        exc_cells['type'] = 'exc'
        exc_cells['Layer'] = n+1
        
        
        # Lectura inhibitoria
        inh = __load_meter_data(folder_path, file2, t_presim_value, t_sim_value + t_presim_value)
        cellids, times = zip(*inh[2][0])
        inh_cells = pd.DataFrame({'cellid': cellids, 'time': times})
        inh_cells['type'] = 'inh'
        inh_cells['Layer'] = n+1
        cell_info = pd.concat([inh_cells,exc_cells],axis=0)
        
        info.append(cell_info)
        
    info_total = pd.concat(info,axis=0)
    return info_total,times_simulation




def apliccation_metrics(folder_path, archivos_spike_recorder):
    

    # Llama a la función para obtener los archivos que comienzan con "spike_recorder"
    archivos_spike_recorder = select_spike_recorder_files(folder_path)
    info_total,times = process_files_in_pairs_positions(folder_path, archivos_spike_recorder)
    
    # Mapear las capas a los nuevos nombres
    layer_mapping = {1: '2/3', 2: '4', 3: '5', 4: '6'}
    info_total['Layer'] = info_total['Layer'].map(layer_mapping)
    
    # Crear un histograma por cada combinación de type y Layer
    unique_combinations = info_total[['type', 'Layer']].drop_duplicates()

    # Número de combinaciones únicas
    num_combinations = len(unique_combinations)

        # Configurar el diseño de subplots
    num_rows = num_combinations
    num_cols = 1

    # Crear subplots
    fig, axs = plt.subplots(num_rows, num_cols, figsize=(8, 4*num_rows))

    # Iterar sobre cada combinación única
    for i, row in enumerate(unique_combinations.itertuples(), 1):
        subset = info_total[(info_total['type'] == row.type) & (info_total['Layer'] == row.Layer)]

        # Configurar la ubicación de la subfigura actual
        if num_rows > 1:
            ax = axs[i-1]
        else:
            ax = axs

        # Asignar colores según el tipo
        color = '#595289' if row.type == 'exc' else '#af143c'
        
        # Crear el histograma en la subfigura actual con colores personalizados
        ax.hist(subset['time'], bins=range(int(subset['time'].min()), int(subset['time'].max()) + 11, 5), alpha=0.7, label=f"{row.type}, Layer {row.Layer}", color=color)

       
        # Configurar etiquetas y título
        ax.set_xlabel('Time')
        ax.set_ylabel('Frequency')
        ax.set_title(f'Histogram - {row.type}, Layer {row.Layer}')
        ax.legend()

        # Ajustar el espaciado entre subplots para evitar superposiciones
        plt.tight_layout()

        # Guardar la figura en un archivo
    plt.savefig(folder_path + "/spike_time_histogram.png")

                

    
id_result = '20231206222524' # Modelo de un microcircuito
path_result = 'results/potjans_diesmann/'+id_result+'/'


# Llama a la función para obtener los archivos que comienzan con "spike_recorder"
archivos_spike_recorder = select_spike_recorder_files(path_result)
apliccation_metrics(path_result, archivos_spike_recorder)





