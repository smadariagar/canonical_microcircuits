import os
import json
import random
import math

import pandas as pd
import numpy as np
import datetime
import warnings
import matplotlib.pyplot as plt
from scipy.fft import fft

from assets.potjans_diesmann.sim_params import sim_dict
import tools.histogram_single_microcircuit as hist_spikes
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


def calc_lfp(cells_dict, tau, lfp_time, delay, amp):
    """Calculate LFP using a temporal kernel."""
    lfp = np.zeros(lfp_time.shape)
    for cell in cells_dict:
        # Usar claves del diccionario en lugar de posiciones
        t_diff = lfp_time - delay[cell["new_cellid"]] - cell["time"]
        temporal_kernel = np.exp(-t_diff ** 2 / tau)
        
        # Accumulate LFP contributions directly
        lfp += amp[None, cell["new_cellid"]] * temporal_kernel
    return lfp


def metrics(inh_cells, exc_cells, t_sim):
    """
    Calcula el LFP para una geometría 2D plana.
    Versión corregida para ser compatible con calc_lfp.
    """
    # --- PASO 1: Calcular Ne, Ni ---
    Ne = len(exc_cells['cellid'].unique())
    Ni = len(inh_cells['cellid'].unique())
    N = Ne + Ni

    if Ne == 0 or Ni == 0:
        print("No hay suficientes neuronas para calcular el LFP.")
        return np.zeros(int(t_sim / 0.05)), None, None

    # --- PASO 2: Re-indexar a 'new_cellid' (ESTO FALTABA) ---
    exc_id_map = {old_id: new_id for new_id, old_id in enumerate(exc_cells['cellid'].unique())}
    inh_id_map = {old_id: new_id + Ne for new_id, old_id in enumerate(inh_cells['cellid'].unique())}

    exc_cells['new_cellid'] = exc_cells['cellid'].map(exc_id_map)
    inh_cells['new_cellid'] = inh_cells['cellid'].map(inh_id_map)

    # --- PASO 3: Crear geometría 2D y calcular LFP ---
    xmax, ymax = 0.2, 0.2
    X = np.random.uniform(0, xmax, N)
    Y = np.random.uniform(0, ymax, N)
    
    dt = 0.05
    npts = int(t_sim / dt)
    xe, ye = xmax / 2, ymax / 2

    va = 200.0
    lambda_ = 0.2
    sig_i = 2.1
    sig_e = 1.5 * sig_i
    # Seleccionar la amplitud para la capa deseada (ej. soma)
    amp_e = 0.48
    amp_i = 3.0

    dist = np.sqrt((X - xe)**2 + (Y - ye)**2)
    delay = 10.4 + dist / va
    amp = np.exp(-dist / lambda_)
    
    amp[:Ne] *= amp_e
    amp[Ne:] *= amp_i

    s_e = 2 * sig_e * sig_e
    s_i = 2 * sig_i * sig_i
    lfp_time = np.arange(npts) * dt

    print("Calculando LFP (método plano 2D)...")
    
    # --- CORRECCIÓN AQUÍ: Usar .to_dict('records') ---
    lfp_inh = calc_lfp(inh_cells.to_dict('records'), s_i, lfp_time, delay, amp)
    lfp_exc = calc_lfp(exc_cells.to_dict('records'), s_e, lfp_time, delay, amp)

    total_lfp = lfp_inh + lfp_exc
    
    # El return original tenía más elementos, lo ajustamos
    return total_lfp, lfp_time, npts


def metrics_esferic(inh_cells, exc_cells, t_sim):
    """
    Calcula el LFP esférico. Recibe DataFrames con posiciones 3D,
    y se encarga de definir el electrodo, calcular distancias y filtrar.
    """
    # --- PASO 1: Definir la esfera de medición ---
    sphere_radius = 0.3
    center_x, center_y, center_z = 0.1, 0.1, 0.1

    # --- PASO 2: Calcular distancia y filtrar neuronas dentro de la esfera ---
    exc_cells['distance_to_center'] = np.sqrt((exc_cells['x'] - center_x)**2 + (exc_cells['y'] - center_y)**2 + (exc_cells['z'] - center_z)**2)
    inh_cells['distance_to_center'] = np.sqrt((inh_cells['x'] - center_x)**2 + (inh_cells['y'] - center_y)**2 + (inh_cells['z'] - center_z)**2)
    
    exc_in_sphere = exc_cells[exc_cells['distance_to_center'] <= sphere_radius].copy()
    inh_in_sphere = inh_cells[inh_cells['distance_to_center'] <= sphere_radius].copy()

    # --- PASO 3: Calcular Ne, Ni y re-indexar a 'new_cellid' ---
    Ne = len(exc_in_sphere['cellid'].unique())
    Ni = len(inh_in_sphere['cellid'].unique())

    if Ne == 0 or Ni == 0:
        print("No hay suficientes neuronas en la esfera para calcular el LFP.")
        return np.zeros(int(t_sim / 0.05)), None, None # Devuelve un LFP vacío

    exc_id_map = {old_id: new_id for new_id, old_id in enumerate(exc_in_sphere['cellid'].unique())}
    inh_id_map = {old_id: new_id + Ne for new_id, old_id in enumerate(inh_in_sphere['cellid'].unique())}

    exc_in_sphere['new_cellid'] = exc_in_sphere['cellid'].map(exc_id_map)
    inh_in_sphere['new_cellid'] = inh_in_sphere['cellid'].map(inh_id_map)
    
    # PASO 3: Definir parámetros y extraer distancias
    dt = 0.05
    npts = int(t_sim / dt)
    va = 200.0
    lambda_ = 0.2
    sig_i = 2.1
    sig_e = 1.5 * sig_i
    amp_e = 0.48
    amp_i = 3.0
    
    dist_exc = exc_in_sphere.drop_duplicates(subset='new_cellid').sort_values('new_cellid')['distance_to_center'].to_numpy()
    dist_inh = inh_in_sphere.drop_duplicates(subset='new_cellid').sort_values('new_cellid')['distance_to_center'].to_numpy()
    
    dist = np.concatenate((dist_exc, dist_inh))

    delay = 10.4 + dist / va
    amp = np.exp(-dist / lambda_)
    
    # La lógica de aplicar amplitudes ahora es consistente porque Ne y Ni son correctos
    amp[:Ne] *= amp_e
    amp[Ne:] *= amp_i

    # PASO 4: Calcular LFP
    s_e = 2 * sig_e * sig_e
    s_i = 2 * sig_i * sig_i
    lfp_time = np.arange(npts) * dt

    lfp_exc = calc_lfp(exc_in_sphere.to_dict('records'), s_e, lfp_time, delay, amp)
    lfp_inh = calc_lfp(inh_in_sphere.to_dict('records'), s_i, lfp_time, delay, amp)
    
    total_lfp = lfp_exc + lfp_inh
    
    return total_lfp, lfp_time, npts


def process_files_in_pairs(folder_path, spike_recorder_files):
    """
    Process files in pairs and perform operations using extracted information.

    Args:
        folder_path (str): The path to the folder.
        spike_recorder_files (list): List of spike recorder file names.
    """
    if len(spike_recorder_files) % 2 != 0:
        print("Number of files is not even")
        return

    with open(os.path.join(folder_path, 'sim_params.json'), 'r') as file:
        sim_dict = json.load(file)
    local_num_threads = sim_dict.get("local_num_threads")
    t_sim_value = sim_dict.get("t_sim")
    t_presim_value = 0

    height = 0.2 #diferencia de altura entre capas en mm
    radius = 0.2  # Size of the array (in mm)

    for n, i in enumerate(range(0, len(spike_recorder_files), local_num_threads*2)):

        if n > 3:
            continue

        exc_cells_tot = pd.DataFrame()
        inh_cells_tot = pd.DataFrame()

        for j in range(local_num_threads):

            file1 = spike_recorder_files[i+j]
            file2 = spike_recorder_files[i+j+local_num_threads]

            exc = __load_meter_data(folder_path, file1, t_presim_value, t_sim_value + t_presim_value)
            cellids, times = zip(*exc[2][0])
            exc_cells = pd.DataFrame({'cellid': cellids, 'time': times})
            exc_cells['type'] = 'exc'
            exc_cells['Layer'] = n
            
            inh = __load_meter_data(folder_path, file2, t_presim_value, t_sim_value + t_presim_value)
            cellids, times = zip(*inh[2][0])
            inh_cells = pd.DataFrame({'cellid': cellids, 'time': times})
            inh_cells['type'] = 'inh'
            inh_cells['Layer'] = n

            exc_cells_tot = pd.concat([exc_cells_tot, exc_cells], axis=0)
            inh_cells_tot = pd.concat([inh_cells_tot, inh_cells], axis=0)

       # --- PASO 2: Asignación de posiciones 3D (Unificada) ---
        # Obtener todos los IDs únicos de la capa
        all_unique_ids = pd.concat([exc_cells_tot['cellid'], inh_cells_tot['cellid']]).unique()
        
        # Generar posiciones para todos los IDs únicos UNA SOLA VEZ
        positions_df = assign_positions_to_cells(all_unique_ids, height, radius)
        
        # Unir las posiciones a los dataframes de spikes
        exc_cells_con_pos = pd.merge(exc_cells_tot, positions_df, on='cellid', how='left')
        inh_cells_con_pos = pd.merge(inh_cells_tot, positions_df, on='cellid', how='left')

        # --- PASO 3: Llamada a la función de cálculo ---
        # Ya no se necesita Ne, Ni o correc_id aquí.
        # La función metrics_esferic se encargará de todo.

        lfp_capa, lfp_time, npts = metrics(
            inh_cells=inh_cells_tot, 
            exc_cells=exc_cells_tot, 
            t_sim=t_sim_value
        )
        
        np.savetxt(os.path.join(folder_path, str('lfp_layer_' + str(n+1) + '.csv')), lfp_capa, delimiter=',')
        print('LFP capa ' + str(n+1))

        lfp_capa, lfp_time, npts = metrics_esferic(
            inh_cells=inh_cells_con_pos, 
            exc_cells=exc_cells_con_pos, 
            t_sim=t_sim_value
        )
        
        np.savetxt(os.path.join(folder_path, str('lfp_layer_sph_' + str(n+1) + '.csv')), lfp_capa, delimiter=',')
        print('LFP capa ' + str(n+1))


def assign_positions_to_cells(cell_ids, height, radius):
    n_points = len(cell_ids)
    angles = np.random.uniform(0, 2 * math.pi, n_points)
    radii = np.random.uniform(0, radius, n_points)
    positions_df = pd.DataFrame({
        'cellid': cell_ids,
        'x': radii * np.cos(angles),
        'y': radii * np.sin(angles),
        'z': np.random.uniform(0, height, n_points)
    })
    return positions_df


def get_lfp(path):

     # Read JSONs
    with open(os.path.join(path, 'net_params.json'), 'r') as file:
        net_dict = json.load(file)
    num_neurons    = net_dict.get('full_num_neurons_v1')
    num_neurons_v2 = net_dict.get('full_num_neurons_v2')
    N_scaling      = net_dict.get("N_scaling")
    K_scaling      = net_dict.get("K_scaling")

    with open(os.path.join(path, 'sim_params.json'), 'r') as file:
        sim_dict = json.load(file)
    local_num_threads = sim_dict.get("local_num_threads")
    t_sim = sim_dict.get("t_sim")

    # Add columns names
    cols = np.array(['folder', 'layer', 'type'])
    params = range(int(t_sim/10))
    names = np.concatenate((cols, params), axis=None)
    hist_data = pd.DataFrame(columns=names)

    num_neurons = num_neurons+num_neurons+num_neurons+num_neurons+num_neurons_v2+num_neurons_v2

    archivos_spike_recorder = hist_spikes.select_spike_recorder_files(path)
    print(archivos_spike_recorder)
    info_total, times = hist_spikes.process_files_in_pairs_positions(path, archivos_spike_recorder)
    tiempos = info_total.iloc[:,1]
    info_total['time'] = tiempos


