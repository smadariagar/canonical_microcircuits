
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
    points_inside_sphere = points_inside_sphere[['cellid', 'distance_to_center','x','y']]

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



def process_files_in_pairs_positions_multiple(folder_path, diccionario_micro,height, radius):
    """
    Process files in pairs and perform operations using extracted information.

    Args:
        folder_path (str): The path to the folder.
        spike_recorder_files (list): List of spike recorder file names.
    """
    
    info_total = []
    for k  in range(len(diccionario_micro)):
        spike_recorder_files = diccionario_micro[k]
        if len(spike_recorder_files) % 2 != 0:
            print("Number of files is not even.")
            return
        info = []
        n = 0
        times_simulation = []
        for i in range(0,  len(spike_recorder_files), 2):
            
            # Lectura de parámetros de simulacion
            file1 = spike_recorder_files[i]
            file2 = spike_recorder_files[i + 1]
            t_presim_value, t_sim_value = extract_time_info(folder_path + 'sim_params.json')
            t_presim_value = 0
            times_simulation.append([t_presim_value, t_sim_value])
            
            # Lectura excitatoria
            exc = __load_meter_data(folder_path, file1, t_presim_value, t_sim_value + t_presim_value)
            exc_cellids, times = zip(*exc[2][0])
            exc_cells = pd.DataFrame({'cellid': exc_cellids, 'time': times})
            exc_cells['type'] = 'exc'
            Ne = (exc[1][i][1] - exc[1][i][0]) + 1
            
            
            # Lectura inhibitoria
            inh = __load_meter_data(folder_path, file2, t_presim_value, t_sim_value + t_presim_value)
            inh_cellids, times = zip(*inh[2][0])
            inh_cells = pd.DataFrame({'cellid': inh_cellids, 'time': times})
            inh_cells['type'] = 'inh'
            Ni = (inh[1][i+1][1] - inh[1][i+1][0]) + 1
                
            cell_info = pd.concat([inh_cells,exc_cells],axis=0)
      
            # Se asigna posiciones
            exc_cell_ids = exc_cells['cellid'].unique().tolist()
            inh_cell_ids = inh_cells['cellid'].unique().tolist()
            generated_points_df = generate_random_unique_points(Ni+Ne, exc_cell_ids, inh_cell_ids,height, radius)
            generated_points_df['z'] = generated_points_df['z']+ height*(n)
            generated_points_df['Layer'] = (n+1)
            generated_points_df['Microcircuito'] = k+1
            generated_points_df['x'] = generated_points_df['x'] + k*radius*2
            info.append(cell_info.merge(generated_points_df,on='cellid'))
            n = n + 1
        
        
        info_microcircuito = pd.concat(info,axis=0)
        info_total.append(info_microcircuito)
    info_total = pd.concat(info_total,axis=0)
    return info_total,times_simulation


def apliccation_metrics(folder_path, archivos_spike_recorder):
    
    height = 0.2 #diferencia de altura entre capas en mm
    radius = 0.2  # Size of the array (in mm)
    sphere_radius = 0.3
    # Llama a la función para obtener los archivos que comienzan con "spike_recorder"
    archivos_spike_recorder = select_spike_recorder_files(folder_path)
    # Se divide la lista de archivos en 2 microcircuitos
    # Función lambda para obtener el valor numérico de cada elemento
    get_valor = lambda x: int(x.split('-')[1])
    # Ordenar la lista por el valor numérico
    archivos_spike_recorder_ordenados = sorted(archivos_spike_recorder, key=get_valor)
    # Calcular la mitad de la longitud de la lista
    mitad_longitud = len(archivos_spike_recorder_ordenados) // 2
    # Dividir la lista en dos partes de igual longitud
    primer_microcircuito = archivos_spike_recorder_ordenados[:mitad_longitud]
    segundo_microcircuito = archivos_spike_recorder_ordenados[mitad_longitud:]
    
    # Generar el diccionario con sublistas
    diccionario_spike = {0: primer_microcircuito , 1: segundo_microcircuito }
    
    info_total,times = process_files_in_pairs_positions_multiple(folder_path, diccionario_spike,height,radius)
    name_capa = ['2-3','4','5','6']
    for n,i in enumerate(info_total['Layer'].unique()):
        # Desde el microcircuito 1 al 2
        center_x = center_y = 0
        center_z = (height/2)+(n*height)
        cell_inside = points_inside_sphere(info_total, center_x, center_y,center_z, sphere_radius)

        cell_layer = cell_inside.merge(info_total,on=['cellid','x','y'])
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
        
      
        fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

        # Filtrar las celdas según las condiciones dadas
        exc_micro_1 = exc_cells[(exc_cells['type'] == 'exc') & (exc_cells['Microcircuito'] == 1)]
        exc_micro_2 = exc_cells[(exc_cells['type'] == 'exc') & (exc_cells['Microcircuito'] == 2)]

        
        inh_micro_1 = inh_cells[(inh_cells['type'] == 'inh') & (inh_cells['Microcircuito'] == 1)]
        inh_micro_2 = inh_cells[(inh_cells['type'] == 'inh') & (inh_cells['Microcircuito'] == 2)]

        Nstp = 1  # step cell to draw
        fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)
        fs = 18  # fontsize
        max = cell_layer['cellid'].max()
        exc_micro_1["cellid"] = (exc_micro_1["cellid"]-max)
        exc_micro_2["cellid"] = (exc_micro_2["cellid"]-max)
        inh_micro_1["cellid"] = (inh_micro_1["cellid"]-max)
        inh_micro_2["cellid"] = (inh_micro_2["cellid"]-max)
        exc_micro_1["cellid"] = exc_micro_1["cellid"].abs()+1
        exc_micro_2["cellid"] = exc_micro_2["cellid"].abs()+1
        inh_micro_1["cellid"] = inh_micro_1["cellid"].abs()+1
        inh_micro_2["cellid"] = inh_micro_2["cellid"].abs()+1
   
        
        axes[0].plot(exc_micro_1[::Nstp]["time"], exc_micro_1[::Nstp]["cellid"], ".", color='#595289', label='Exc Microcircuit 1')
        axes[0].plot(exc_micro_2[::Nstp]["time"], exc_micro_2[::Nstp]["cellid"], ".", color='#595289', label='Exc Microcircuit 2')

        # Inhibitorias
        axes[0].plot(inh_micro_1[::Nstp]["time"], inh_micro_1[::Nstp]["cellid"], ".", color='#af143c', label='Inh Microcircuit 1')
        axes[0].plot(inh_micro_2[::Nstp]["time"], inh_micro_2[::Nstp]["cellid"], ".", color='#af143c', label='Inh Microcircuit 2')
        
        #Promedios cellid por capa
        prom_inh_1 = inh_micro_1.groupby(['type','Microcircuito','Layer'])['cellid'].mean().reset_index()
        prom_inh_2 = inh_micro_2.groupby(['type','Microcircuito','Layer'])['cellid'].mean().reset_index()
        prom_exc_1 = exc_micro_1.groupby(['type','Microcircuito','Layer'])['cellid'].mean().reset_index()
        prom_exc_2 = exc_micro_2.groupby(['type','Microcircuito','Layer'])['cellid'].mean().reset_index()
        cellid_prom = pd.concat([prom_inh_1,prom_inh_2,prom_exc_1,prom_exc_2], ignore_index=True)

        names_capas = {
            'type': ['inh', 'inh', 'inh', 'inh', 'exc', 'exc', 'exc', 'exc', 'inh', 'inh', 'inh', 'inh',  'exc', 'exc', 'exc', 'exc'],
            'Microcircuito': [1, 1, 1, 1, 1, 1, 1, 1, 2, 2, 2, 2, 2, 2, 2, 2],
            'Layer': [1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4, 1, 2, 3, 4],
            'name': ['L2/3I_src', 'L4I_src', 'L5I_src', 'L6I_src', 'L2/3E_src', 'L4E_src', 'L5E_src', 'L6E_src', 'L2/3I_tg', 'L4I_tg', 'L5I_tg', 'L6I_tg', 'L2/3E_tg', 'L4E_tg', 'L5E_tg', 'L6E_tg']
        }

        capas = pd.DataFrame(names_capas)
        ticks = capas.merge(cellid_prom,on=['type','Microcircuito','Layer'])
        ticks = ticks.sort_values(by='cellid',ascending=False)
                
        y_labels = list(ticks['cellid'])
        y_tick_labels = list(ticks['name'])
        axes[0].set_yticks(y_labels)
        axes[0].set_yticklabels(y_tick_labels, fontsize=fs)

        minimo = np.partition(list(inh_cells["time"]), 4)[4]
        axes[1].plot(lfp_time, lfp_capa,color='black', linewidth=2.0)
        axes[1].set_xlabel('time [ms]', fontsize=fs)
        axes[1].set_ylabel('Voltage [µV]', fontsize=fs)
        axes[1].tick_params(axis='x', labelsize=fs) 
        axes[1].tick_params(axis='y', labelsize=fs) 
        axes[1].set_xlim(minimo-20, np.max(exc_cells[::Nstp]["time"])+20)
        
        fig.tight_layout()
        #plt.xlim(100,500)


        # prettify graph
        axes[0].spines["top"].set_visible(False)
        axes[0].spines["right"].set_visible(False)
        axes[1].spines["top"].set_visible(False)
        axes[1].spines["right"].set_visible(False)
        plt.legend()
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
        plt.xlim(2,120)
        plt.savefig(folder_path+'Espectro_esferica__'+name_capa[n]+'_microcircuitos.png')



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
        
 
id_result = '20231206171628' # Modelo de 2 microcircuitos
path_result = 'results/potjans_diesmann/'+id_result+'/'


# Llama a la función para obtener los archivos que comienzan con "spike_recorder"
archivos_spike_recorder = select_spike_recorder_files(path_result)
apliccation_metrics(path_result, archivos_spike_recorder)





