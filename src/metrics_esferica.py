
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
    
def generate_random_unique_points(N, exc_cell_ids, inh_cell_ids, height, radius):
    points = set()  # Use a set to ensure unique positions

    for cell_id in exc_cell_ids + inh_cell_ids:
        while True:
            angle = random.uniform(0, 2 * math.pi)
            radius_value = random.uniform(0, radius)
            x, y = radius_value * math.cos(angle), radius_value * math.sin(angle)
            z = random.uniform(0, height)
            if (cell_id, x, y, z) not in points:
                points.add((cell_id, x, y, z))
                break

    # Convert the set of points to a DataFrame
    df = pd.DataFrame(list(points), columns=['cellid', 'x', 'y', 'z'])
    return df

def points_inside_sphere(cell_info, center_x, center_y,center_z, sphere_radius):
    df = cell_info.copy()
    # Calculate the Euclidean distance from (x, y, z) to the sphere's center
    df['distance_to_center'] = np.sqrt((df['x'] - center_x) ** 2 +
                                               (df['y'] - center_y) ** 2 +
                                               (df['z'] - center_z) ** 2)

    # Filter the points that fall within the sphere (distance <= radius)
    points_inside_sphere = df[df['distance_to_center'] <= sphere_radius]

    # Select the columns of interest
    points_inside_sphere = points_inside_sphere[['cellid', 'distance_to_center']]

    return points_inside_sphere.drop_duplicates()

    
        

def calc_lfp(cells, tau,lfp_time,delay,amp):
    """Calculate LFP using a temporal kernel."""
 
    lfp = np.zeros(lfp_time.shape)
    
    for idx in range(len(cells["new_cellid"])):
        # Calculate temporal kernel
        t_diff = lfp_time - delay[cells["new_cellid"][idx]] - cells["time"][idx]
        temporal_kernel = np.exp(-t_diff ** 2 / tau)
        
        # Accumulate LFP contributions directly
        lfp += amp[None, cells["new_cellid"][idx]] * temporal_kernel
    return lfp


def metrics(tmin ,tmax, inh_cells,exc_cells,Ne,Ni):
    inh_df = inh_cells.copy()
    exc_df = exc_cells.copy()
    # Crear un mapeo de cellid único a nuevo cellid
    unique_cellids = exc_df['cellid'].unique()
    cellid_mapping = {cellid: idx for idx, cellid in enumerate(unique_cellids)}
    # Aplicar la transformación al DataFrame
    exc_df['new_cellid'] = exc_df['cellid'].map(cellid_mapping)
    id_base =  exc_df['new_cellid'].iloc[-1]
    
    # Crear un mapeo de cellid único a nuevo cellid
    unique_cellids = inh_df['cellid'].unique()
    cellid_mapping = {cellid: idx for idx, cellid in enumerate(unique_cellids)}
    # Aplicar la transformación al DataFrame
    inh_df['new_cellid'] = inh_df['cellid'].map(cellid_mapping) + id_base+1


    # adjust time and convert to ms
    inh_df["time"] = inh_df["time"] - tmin
    exc_df["time"] = exc_df["time"] - tmin


    # 4. calculate LFP
    dt = 0.01  # time resolution
    npts = int(tmax / dt)  # nb points in LFP vector
    va = 200  # axonal velocity (mm/sec)
    lambda_ = 0.2  # space constant (mm)
    sig_i = 2.1  # std-dev of ihibition (in ms)
    sig_e = 1.5 * sig_i  # std-dev for excitation
    amp_e = 0.48  # exc uLFP amplitude (soma layer)
    amp_i = 3  # inh uLFP amplitude (soma layer)

    dist_inh = inh_df['distance_to_center'].unique()
    dist_exc = exc_df['distance_to_center'].unique()# distance to  electrode in mm
    dist =  np.array([*dist_exc,*dist_inh])
    delay = 10.4 + dist / va  # delay to peak (in ms)
    amp = np.exp(-dist / lambda_)
    amp[:Ne] *= amp_e
    amp[Ne:] *= amp_i

    # Calculate LFP
    s_e = 2 * sig_e * sig_e
    s_i = 2 * sig_i * sig_i
    lfp_time = np.arange(npts) * dt
    lfp_inh = calc_lfp(inh_df, s_i, lfp_time, delay, amp)
    lfp_exc = calc_lfp(exc_df, s_e, lfp_time, delay, amp)
    total_lfp = lfp_inh + lfp_exc

    
    return total_lfp , lfp_time,npts



def process_files_in_pairs_positions(folder_path, spike_recorder_files,height, radius):
    """
    Process files in pairs and perform operations using extracted information.

    Args:
        folder_path (str): The path to the folder.
        spike_recorder_files (list): List of spike recorder file names.
    """
    if len(spike_recorder_files) % 2 != 0:
        print("Number of files is not even.")
        return
    
    n = 0
    info = []
    times_simulation = []
    for i in range(0,  len(spike_recorder_files), 2):
        
        # Lectura de parámetros de simulacion
        file1 = spike_recorder_files[i]
        file2 = spike_recorder_files[i + 1]
        t_presim_value, t_sim_value = extract_time_info(folder_path + 'sim_params.json')
        times_simulation.append([t_presim_value, t_sim_value])
        
        # Lectura excitatoria
        exc = __load_meter_data(folder_path, file1, t_presim_value, t_sim_value + t_presim_value)
        cellids, times = zip(*exc[2][0])
        exc_cells = pd.DataFrame({'cellid': cellids, 'time': times})
        exc_cells['type'] = 'exc'
        Ne = (exc[1][i][1] - exc[1][i][0]) + 1
        
        
        # Lectura inhibitoria
        inh = __load_meter_data(folder_path, file2, t_presim_value, t_sim_value + t_presim_value)
        cellids, times = zip(*inh[2][0])
        inh_cells = pd.DataFrame({'cellid': cellids, 'time': times})
        inh_cells['type'] = 'inh'
        Ni = (inh[1][i+1][1] - inh[1][i+1][0]) + 1
        cell_info = pd.concat([inh_cells,exc_cells],axis=0)
        
        # Se asigna posiciones
        exc_cell_ids = exc_cells['cellid'].unique().tolist()
        inh_cell_ids = inh_cells['cellid'].unique().tolist()
        generated_points_df = generate_random_unique_points(Ni+Ne, exc_cell_ids, inh_cell_ids,height, radius)
        generated_points_df['z'] = generated_points_df['z']+ height*(n)
        generated_points_df['Layer'] = (n+1)
        info.append(cell_info.merge(generated_points_df,on='cellid'))
        n = n + 1
        
    info_total = pd.concat(info,axis=0)
    return info_total,times_simulation


def apliccation_metrics(folder_path, archivos_spike_recorder):
    
    height = 0.2 #diferencia de altura entre capas en mm
    radius = 0.2  # Size of the array (in mm)
    sphere_radius = 0.2
    # Llama a la función para obtener los archivos que comienzan con "spike_recorder"
    archivos_spike_recorder = select_spike_recorder_files(folder_path)
    info_total,times = process_files_in_pairs_positions(folder_path, archivos_spike_recorder,height,radius)
    name_capa = ['2-3','4','5','6']
    for n,i in enumerate(info_total['Layer'].unique()):
        center_x = center_y = 0
        center_z = (height/2)+(n*height)
        cell_inside = points_inside_sphere(info_total, center_x, center_y,center_z, sphere_radius)
        cell_layer = cell_inside.merge(info_total,on='cellid')
        t_presim_value, t_sim_value = times[n]
        
            # Se reordenan los cellid.
        cell_layer = cell_layer.sort_values('cellid')

        # Crear un mapeo de cellid único a nuevo cellid
        unique_cellids = cell_layer['cellid'].unique()
        cellid_mapping = {cellid: idx for idx, cellid in enumerate(unique_cellids)}

        # Aplicar la transformación al DataFrame
        cell_layer['new_cellid'] = cell_layer['cellid'].map(cellid_mapping)
        
        inh_cells = cell_layer[cell_layer['type']=='inh'].reset_index(drop=True)
        exc_cells = cell_layer[cell_layer['type']=='exc'].reset_index(drop=True)
        Ni = len(inh_cells['new_cellid'].unique())
        Ne = len(exc_cells['new_cellid'].unique())

    
        lfp_capa, lfp_time,npts = metrics(t_presim_value ,t_sim_value, 
                           inh_cells, exc_cells, Ne, Ni)
        
        Nstp = 5  # step cell to draw
        tick_size = 5

        fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

        axes[0].plot(exc_cells[::Nstp]["time"]-t_presim_value, exc_cells[::Nstp]["cellid"], ".", ms=tick_size)
        axes[0].plot(inh_cells[::Nstp]["time"]-t_presim_value, inh_cells[::Nstp]["cellid"], ".", ms=tick_size)


        axes[1].plot(lfp_time, lfp_capa)
        axes[1].set_xlabel("time, ms")
        axes[1].set_xlim(0, t_sim_value)

        # prettify graph
        axes[0].spines["top"].set_visible(False)
        axes[0].spines["right"].set_visible(False)
        axes[1].spines["top"].set_visible(False)
        axes[1].spines["right"].set_visible(False)
        plt.savefig(folder_path+"/demo_lfp_kernel_esferica_capa_"+name_capa[n]+"_microcircuitos.pdf")
        
        
                
        # Configuración de la señal
        fs = npts  # Frecuencia de muestreo en Hz


        # Calcular la transformada de Fourier de la señal
        spectrum = fft(lfp_capa)

        # Calcular las frecuencias correspondientes al espectro
        frequencies = np.fft.fftfreq(len(lfp_capa), 1/fs)

        # Graficar el espectro de frecuencia
        plt.figure(figsize=(10, 6))
        plt.plot(frequencies, np.abs(spectrum))
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Amplitud')
        plt.title('Espectro de Frecuencia')
        plt.xlim(1,120)
        plt.savefig(folder_path+'Espectro_esferica'+name_capa[n]+'.png')



        plt.figure(figsize=(10, 6))
        plt.semilogx(frequencies, 20 * np.log10(np.abs(spectrum)))  # Escala logarítmica en el eje x y y
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Amplitud (dB)')
        plt.xlim(0,500)
        plt.title('Espectro de Frecuencia esférica(Escala Logarítmica en x y y)')
        plt.grid()
        plt.savefig(folder_path+'Espectro_log_esferica_'+name_capa[n]+'_microcircuitos.png')
               
        print('LFP capa '+name_capa[n])          
        n = n + 1
        
        
        

                

    
id_result = '20230713131858' # Modelo d eun microcircuito
path_result = 'results/potjans_diesmann/'+id_result+'/'


# Llama a la función para obtener los archivos que comienzan con "spike_recorder"
archivos_spike_recorder = select_spike_recorder_files(path_result)
apliccation_metrics(path_result, archivos_spike_recorder)





