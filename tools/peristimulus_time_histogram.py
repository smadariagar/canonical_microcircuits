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
import tools.histogram_single_microcircuit as hist_spikes


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

        print(file1)
        print(file2)
        
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
    print(archivos_spike_recorder)
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


def PSTH_folders_data(path, scaling, t_sim, l_bin):
    """
    Sálvenme
    """

    new_df = []

    for folder in os.listdir(path):
        trial_path = os.path.join(path, folder)
        
        if not os.path.isdir(trial_path):
            continue
        print(trial_path)

        if not os.path.exists(os.path.join(trial_path, 'psth_'+str(l_bin)+'.csv')):
            PSTH_data(trial_path, scaling, t_sim, l_bin)

        # Add columns names
        cols = np.array(['folder', 'layer', 'type'])
        params = range(int(t_sim/l_bin))
        names = np.concatenate((cols, params), axis=None)

        df = pd.read_csv(os.path.join(trial_path, 'psth_'+str(l_bin)+'.csv'), header=None, names=names)

        if len(new_df)==0:
            new_df = df
        else:
            new_df = pd.concat([new_df, df], axis=0)

    new_df.to_csv(os.path.join(path, 'psth_'+str(l_bin)+'.csv'), mode='w', index=False, header=False)



def PSTH_data(path, scaling, t_sim, l_bin):
    """
    Help me
    """

    # Add columns names
    cols = np.array(['folder', 'layer', 'type'])
    params = range(int(t_sim/l_bin))
    names = np.concatenate((cols, params), axis=None)
    hist_data = pd.DataFrame(columns=names)

    # Read JSON
    with open(os.path.join(path, 'net_params.json'), 'r') as file:
        net_dict = json.load(file)
    num_neurons = net_dict['full_num_neurons_v1']
    num_neurons_v2 = net_dict['full_num_neurons_v2']

    num_neurons = num_neurons+num_neurons+num_neurons+num_neurons+num_neurons_v2+num_neurons_v2

    archivos_spike_recorder = hist_spikes.select_spike_recorder_files(path)
    info_total, times = hist_spikes.process_files_in_pairs_positions(path, archivos_spike_recorder)
    tiempos = info_total.iloc[:,1]
    info_total['time'] = tiempos

    # Mapear las capas a los nuevos nombres
    layer_mapping = {
        0: '2/3a', 1: '4a', 2: '5a', 3: '6a',
        4: '2/3b', 5: '4b', 6: '5b', 7: '6b',
        8: '2/3c', 9: '4c', 10: '5c', 11: '6c',
        12: '2/3d', 13: '4d', 14: '5d', 15: '6d',
        16: '2/3v2', 17: '4v2', 18: '5v2', 19: '6v2',
        20: '2/3v22', 21: '4v22', 22: '5v22', 23: '6v22',}
    
    info_total['Layer'] = info_total['Layer'].map(layer_mapping)
    
    # Crear un histograma por cada combinación de type y Layer
    unique_combinations = info_total[['type', 'Layer']].drop_duplicates()

    # Iterar sobre cada combinación única
    for i, row in enumerate(unique_combinations.itertuples()):
        
        subset = info_total[(info_total['type'] == row.type) & (info_total['Layer'] == row.Layer)]

        # Crear el histograma en la subfigura actual con colores personalizados
        hist, bin_edges = np.histogram(subset['time'], bins=range(0, int(t_sim)+l_bin, l_bin))
        hist = hist * (1000/l_bin) / (num_neurons[i]*scaling)
 
        hist_data.loc[len(hist_data.index)] = np.concatenate(([path, row.Layer, row.type] , hist), axis=None)
    
    hist_data.to_csv(os.path.join(path, 'psth_'+str(l_bin)+'.csv'), mode='a', index=False, header=False)


def get_data(path, t_sim, l_bin, layer, n_type):
    """
    Help me
    """

    # Add columns names
    cols = np.array(['folder', 'layer', 'type'])
    params = range(int(t_sim/l_bin))
    names = np.concatenate((cols, params), axis=None)

    df = pd.read_csv(os.path.join(path, 'psth_'+str(l_bin)+'.csv'), header=None, names=names)

    m = df.columns.to_list()
    performance = df[(df['layer']==layer) & (df['type']==n_type)][m[3:]].values

    try:
        return performance[0]
    except Exception:
        return []
    

def PSTH_plot(path, t_sim, l_bin):

    # add columns names
    cols = np.array(['folder', 'layer', 'type'])
    params = range(int(t_sim/l_bin))
    names = np.concatenate((cols, params), axis=None)

    hist_data = pd.read_csv(os.path.join(path, 'psth_'+str(l_bin)+'.csv'), header=None, names=names)
    bin_centers = np.linspace(l_bin/2, t_sim-(l_bin/2), int(t_sim/l_bin))

    # Generate psth
    # Crear un histograma por cada combinación de type y Layer
    unique_combinations = hist_data[['layer', 'type']].drop_duplicates()
    
    # # Iterar sobre cada combinación única
    for i, row in enumerate(unique_combinations.itertuples()):
        
        if row.type == 'exc':
            color = '#0063B2'
        else:
            color = '#b015b6'

        subset = hist_data[(hist_data['type'] == row.type) & (hist_data['layer'] == row.layer)][names[3:]].values
        subset = subset.astype(float)
        
        fig = plt.figure(layout='constrained', figsize=(8,3))

        plt.plot(bin_centers, np.mean(subset,axis=0), '.-', color=color)
        bot, top = plt.ylim()  # return the current ylim
    
        plt.plot([500, 500], [bot, top], 'k--')
        plt.plot([1000, 1000], [bot, top], 'k--')
        #plt.plot([3000, 3000], [bot, top], 'k--')

        plt.title(row.layer+' '+row.type)
        plt.xlabel('time [ms]')
        plt.ylabel('firing rate (spikes/s)')

        plt.show()


def PSTH_plot_tog(path, t_sim, l_bin):

    # add columns names
    cols = np.array(['folder', 'layer', 'type'])
    params = range(int(t_sim/l_bin))
    names = np.concatenate((cols, params), axis=None)

    hist_data = pd.read_csv(os.path.join(path, 'psth_'+str(l_bin)+'.csv'), header=None, names=names)
    bin_centers = np.linspace(l_bin/2, t_sim-(l_bin/2), int(t_sim/l_bin))

    # Generate psth
    # Crear un histograma por cada combinación de type y Layer
    unique_combinations = hist_data[['layer', 'type']].drop_duplicates()
    

    fig, ax = plt.subplots(4,2, layout='constrained', figsize=(14,12), sharex=True)
    ax = ax.flatten()


    # # Iterar sobre cada combinación única
    nmcc = -1
    sym = ['o', '^', '1','x','s','v']
    sy = sym+sym
    for j, row in enumerate(unique_combinations.itertuples()):
        
        if row.type == 'exc':
            color = '#0063B2'
        else:
            color = '#b015b6'

        if j%8==0:
            nmcc = nmcc+1

        subset = hist_data[(hist_data['type'] == row.type) & (hist_data['layer'] == row.layer)][names[3:]].values
        subset = subset.astype(float)
        
        i = j-nmcc*8
        ax[i].plot(bin_centers, np.mean(subset,axis=0), sym[nmcc]+'-', color=color)
        bot, top = ax[i].get_ylim()  # return the current ylim

        ax[i].plot([500, 500], [bot, top], 'k--')
        ax[i].plot([1000, 1000], [bot, top], 'k--')
        ax[i].tick_params(axis='x', labelsize=15)
        ax[i].tick_params(axis='y', labelsize=15) 

    plot_name = 'a_psth_plot.png'
    plt.savefig(os.path.join(path, plot_name), dpi=300)


def PSTH_figure(path, t_sim, l_bin, mcc):

    # add columns names
    cols = np.array(['folder', 'layer', 'type'])
    params = range(int(t_sim/l_bin))
    names = np.concatenate((cols, params), axis=None)

    hist_data = pd.read_csv(os.path.join(path, 'psth_'+str(l_bin)+'.csv'), header=None, names=names)
    bin_centers = np.linspace(l_bin/2, t_sim-(l_bin/2), int(t_sim/l_bin))

    # add columns names
    mean_data = pd.DataFrame(columns=names)
    
    # Generate psth
    # Crear un histograma por cada combinación de type y Layer
    unique_combinations = hist_data[['layer', 'type']].drop_duplicates()

    fig, ax = plt.subplots(4,2, layout='constrained', figsize=(10,8), sharex=True)
    ax = ax.flatten()
    # # Iterar sobre cada combinación única
    nmcc = -1
    for j, row in enumerate(unique_combinations.itertuples()):

        if j%8==0:
            nmcc = nmcc+1
        if nmcc < mcc:
            continue
        if nmcc > mcc:
            break
        if row.type == 'exc':
            color = '#0063B2'
        else:
            color = '#b015b6'

        subset = hist_data[(hist_data['type'] == row.type) & (hist_data['layer'] == row.layer)][names[3:]].values
        subset = subset.astype(float)

        i = j-nmcc*8

        x = bin_centers
        y = np.mean(subset,axis=0)

        ci = np.std(subset,axis=0)#/np.sqrt(len(subset))
        ax[i].plot(bin_centers, np.mean(subset,axis=0), '.-', color=color, markersize=2)
        ax[i].fill_between(bin_centers, (y-ci), (y+ci), color=color, alpha=.1)

        bot, top = ax[i].get_ylim()  # return the current ylim
        ax[i].plot([500, 500], [bot, top], 'k--')
        ax[i].plot([1000, 1000], [bot, top], 'k--')

        ax[i].set_title('Layer '+row.layer[0:-1]+' '+row.type, fontsize=15)
        
        if i%2==0:
            ax[i].set_ylabel('firing rate\n(spikes/s)', fontsize=15)

        if i>5:
            ax[i].set_xlabel('time [ms]', fontsize=15)

        ax[i].tick_params(axis='x', labelsize=15)
        ax[i].tick_params(axis='y', labelsize=15) 

        mean_data.loc[len(mean_data.index)] = np.concatenate((['mean', row.layer, row.type] , y), axis=None)
        mean_data.loc[len(mean_data.index)] = np.concatenate((['std', row.layer, row.type] , ci), axis=None)
    
    #plt.suptitle('Neuronal activity of cortical microcircuit V1 (|)\nwith thalamic input at 20 Hz\n', fontsize=22)
    plot_name = 'psth_'+str(mcc)+'_plot.png'
    plt.savefig(os.path.join(path, plot_name), dpi=300)
    plt.show()

    #if not os.path.exists(os.path.join(path,'mean_'+str(l_bin)+'.csv')):
    mean_data.to_csv(os.path.join(path, 'mean_'+str(l_bin)+'.csv'), mode='a', index=False, header=False)
