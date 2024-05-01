"""_summary_

"""
import os
import json
import pandas as pd
import numpy as np
import warnings
import matplotlib.pyplot as plt

from assets.potjans_diesmann.sim_params import sim_dict 
from utils.helpers import __load_meter_data

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


def process_files_in_pairs_positions(folder_path, spike_recorder_files, k):
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
        
        #t_presim_value, t_sim_value = extract_time_info(folder_path + 'sim_params.json')
        #t_presim_value = 0
        t_presim_value = int(sim_dict["t_presim"])+ 1000.0*k
        t_sim_value = int(sim_dict["t_sim"])+ 1000.0*k
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


def active_neurons(folder_path, k):
    
    # Llama a la función para obtener los archivos que comienzan con "spike_recorder"
    archivos_spike_recorder = select_spike_recorder_files(folder_path)
    info_total,times = process_files_in_pairs_positions(folder_path, archivos_spike_recorder, k)

    # Abrir el archivo .dat en modo lectura
    with open(os.path.join(folder_path,'population_nodeids.dat'), 'r') as file:
        lines = file.readlines()
        matriz = []
        for line in lines:
            # Dividir la línea en elementos individuales y convertirlos a números enteros
            row = [int(x) for x in line.split()]
            matriz.append(row)

    spikes_totales = [0]*matriz[7][1]
    neuron_id = info_total['cellid']
    neuron_id = list(neuron_id.values.tolist())
    times_spikes = info_total['time']
    times_spikes = list(times_spikes.values.tolist())

    for i in range(len(neuron_id)):
        #if indice <= len(spikes_totales):
        indice = neuron_id[i]
        if indice <= matriz[2][1] and indice >= matriz[2][0]:
            #spikes_totales[neuron_id[i]] += 1
            aux_time = times_spikes[i]-k*1000
            if aux_time >= 300 and aux_time <= 400: 
                spikes_totales[neuron_id[i]] += 1
               

    idx = [i for i, x in enumerate(spikes_totales) if x >= 1]
    return idx


def PSTH_maker(folder_path, k, neurons_psth_id):

    # Llama a la función para obtener los archivos que comienzan con "spike_recorder"
    archivos_spike_recorder = select_spike_recorder_files(folder_path)
    info_total,times = process_files_in_pairs_positions(folder_path, archivos_spike_recorder, k)

    neuron_id = info_total['cellid']
    neuron_id = list(neuron_id.values.tolist())
    times_spikes = info_total['time']
    times_spikes = list(times_spikes.values.tolist())

    times_spikes_psth = []
    i = 0
    for indice in neuron_id:
        if indice in neurons_psth_id:
           times_spikes_psth.append(times_spikes[i]-k*1000)
        i=i+1   

    return times_spikes_psth


def PSTH_spikes_trial(path, path_b):
    """
    Sálvenme
    """
    neurons_psth_aux = []

    for f in os.listdir(path):
        if os.path.isdir(os.path.join(path, f)):
            trial_path = os.path.join(path, f)

            neuronas_mas_activas = active_neurons(trial_path, int(f))
            neurons_psth_aux.extend(neuronas_mas_activas)
    
    neurons_psth_aux.sort()
    neurons_psth = []
    [neurons_psth.append(item) for item in neurons_psth_aux if item not in neurons_psth]
    print(neurons_psth)

    all_times_spikes = []
    print(neurons_psth)
    for f in os.listdir(path_b):
        if os.path.isdir(os.path.join(path_b, f)):
            trial_path = os.path.join(path_b, f)

            aux = PSTH_maker(trial_path, int(f), neurons_psth)
            all_times_spikes.extend(aux)

    print(len(all_times_spikes))


    color = '#0063b2'
    n, bins, rects = plt.hist(all_times_spikes, bins=range(0, int(sim_dict["t_sim"]), 4), alpha=1.0, label='aloja', color=color)
    
    m= np.convolve( n, np.ones(10)/10, mode='same')
    print(max(m))
    m=m/max(m)
    plt.show()


    fs = 16
    plt.figure(figsize=(6, 4))
    aa=plt.plot(bins[1:]-5,m,color=color, linewidth=3)
    plt.xlabel('time [ms]', fontsize=fs)
    plt.yticks(fontsize=fs)
    plt.ylim([0.2, 1])
    plt.xticks(fontsize=fs)
    plt.title('Peristimulus time histogram', fontsize=22)
    plt.tight_layout()

    plt.savefig(os.path.join(path_b, 'PSTH.png'), dpi=300)
    plt.show()
    return 0
        


id_result = '20240408173443' # Modelo de un microcircuito
path_result = 'results/potjans_diesmann/'+id_result+'/'

id_result = '20240408173443' # Modelo de un microcircuito
path_B = 'results/potjans_diesmann/'+id_result+'/'

PSTH_spikes_trial(path_result, path_B)
# Llama a la función para obtener los archivos que comienzan con "spike_recorder"
#archivos_spike_recorder = select_spike_recorder_files(path_result)
#apliccation_metrics(path_result, archivos_spike_recorder)
#20240406081551
