import os
from utils.helpers import __load_meter_data
import os
import json
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
    
        

def calc_lfp(cells, tau,lfp_time,delay,amp):
    """Calculate LFP using a temporal kernel."""
 
    lfp = np.zeros(lfp_time.shape)
    
    for idx in range(len(cells["cellid"])):
        # Calculate temporal kernel
        t_diff = lfp_time - delay[cells["cellid"][idx]] - cells["time"][idx]
        temporal_kernel = np.exp(-t_diff ** 2 / tau)
        
        # Accumulate LFP contributions directly
        lfp += amp[None, cells["cellid"][idx]] * temporal_kernel
    return lfp


def metrics(tmin ,tmax, inh_cells,exc_cells,Ne,Ni,correc_id):
    N = Ne+Ni  # nb of cells to consider

    
    inh_cells['cellid'] = inh_cells['cellid'] - correc_id
    exc_cells['cellid'] = exc_cells['cellid'] - correc_id

    # adjust time and convert to ms
    inh_cells["time"] = inh_cells["time"] - tmin
    exc_cells["time"] = exc_cells["time"] - tmin


    # 3. distribute cells in a 2D grid

    xmax = 0.2  # size of the array (in mm)
    ymax = 0.2

    X = np.random.uniform(0, xmax, N)
    Y = np.random.uniform(0, ymax, N)


    # 4. calculate LFP
    #
    # Table of respective amplitudes:
    # Layer   amp_i    amp_e
    # deep    -2       -1.6
    # soma    30       4.8
    # sup     -12      2.4
    # surf    3        -0.8
    #

    dt = 0.01  # time resolution
    npts = int(tmax / dt)  # nb points in LFP vector

    xe = xmax / 2
    ye = ymax / 2  # coordinates of electrode

    va = 200  # axonal velocity (mm/sec)
    lambda_ = 0.2  # space constant (mm)
    dur = 1500 # total duration of LFP waveform
    amp_e = 0.7  # uLFP amplitude for exc cells
    amp_i = -3.4  # uLFP amplitude for inh cells
    sig_i = 2.1  # std-dev of ihibition (in ms)
    sig_e = 1.5 * sig_i  # std-dev for excitation

    # amp_e = -0.16	# exc uLFP amplitude (deep layer)
    # amp_i = -0.2	# inh uLFP amplitude (deep layer)

    amp_e = 0.48  # exc uLFP amplitude (soma layer)
    amp_i = 3  # inh uLFP amplitude (soma layer)

    # amp_e = 0.24	# exc uLFP amplitude (superficial layer)
    # amp_i = -1.2	# inh uLFP amplitude (superficial layer)

    # amp_e = -0.08	# exc uLFP amplitude (surface)
    # amp_i = 0.3	# inh uLFP amplitude (surface)

    dist = np.sqrt((X - xe) ** 2 + (Y - ye) ** 2)  # distance to  electrode in mm
    delay = 10.4 + dist / va  # delay to peak (in ms)
    amp = np.exp(-dist / lambda_)
    amp[:Ne] *= amp_e
    amp[Ne:] *= amp_i

    # Calculate LFP
    s_e = 2 * sig_e * sig_e
    s_i = 2 * sig_i * sig_i
    lfp_time = np.arange(npts) * dt
    lfp_inh = calc_lfp(inh_cells, s_i, lfp_time, delay, amp)
    lfp_exc = calc_lfp(exc_cells, s_e, lfp_time, delay, amp)
    total_lfp = lfp_inh + lfp_exc

    
    return total_lfp ,inh_cells, exc_cells, lfp_time,npts



def process_files_in_pairs(folder_path, spike_recorder_files):
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
    for i in range(0, len(spike_recorder_files), 2):
        file1 = spike_recorder_files[i]
        file2 = spike_recorder_files[i + 1]
        t_presim_value, t_sim_value = extract_time_info(folder_path + 'sim_params.json')
        
        exc = __load_meter_data(folder_path, file1, t_presim_value, t_sim_value + t_presim_value)
        cellids, times = zip(*exc[2][0])
        exc_cells = pd.DataFrame({'cellid': cellids, 'time': times})
        Ne = (exc[1][i][1] - exc[1][i][0]) + 1
        
        inh = __load_meter_data(folder_path, file2, t_presim_value, t_sim_value + t_presim_value)
        cellids, times = zip(*inh[2][0])
        inh_cells = pd.DataFrame({'cellid': cellids, 'time': times})

        Ni = (inh[1][i+1][1] - inh[1][i+1][0]) + 1
        
        
        correc_id = exc[1][i][0]
        lfp_capa,inh_cells, exc_cells, lfp_time,npts = metrics(t_presim_value ,t_sim_value, 
                           inh_cells, exc_cells, Ne, Ni, correc_id)
        
                
        Nstp = 5  # step cell to draw
        tick_size = 5

        fig, axes = plt.subplots(2, 1, figsize=(8, 6), sharex=True)

        axes[0].plot(exc_cells[::Nstp]["time"], exc_cells[::Nstp]["cellid"], ".", ms=tick_size)
        axes[0].plot(inh_cells[::Nstp]["time"], inh_cells[::Nstp]["cellid"], ".", ms=tick_size)


        axes[1].plot(lfp_time, lfp_capa)
        axes[1].set_xlabel("time, ms")
        axes[1].set_xlim(0, t_sim_value)

        # prettify graph
        axes[0].spines["top"].set_visible(False)
        axes[0].spines["right"].set_visible(False)
        axes[1].spines["top"].set_visible(False)
        axes[1].spines["right"].set_visible(False)
        plt.savefig(folder_path+"/demo_lfp_kernel_capa"+str(n+1)+".pdf")
        
        
                
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
        plt.xlim(0,120)
        plt.savefig(folder_path+'Espectro'+str(n+1)+'.png')



        plt.figure(figsize=(10, 6))
        plt.semilogx(frequencies, 20 * np.log10(np.abs(spectrum)))  # Escala logarítmica en el eje x y y
        plt.xlabel('Frecuencia (Hz)')
        plt.ylabel('Amplitud (dB)')
        plt.xlim(0,500)
        plt.title('Espectro de Frecuencia (Escala Logarítmica en x y y)')
        plt.grid()
        plt.savefig(folder_path+'Espectro_log'+str(n+1)+'.png')
               
        print('LFP capa '+str(n+1))            
        n = n + 1
        
        

# '20230901000710'
# Son poisson 20230925000755 error
# Con poisson 20230925001958 rate poisson 8
# Con poisson 20230925002657 rate poisson 20

id_result = '20230925001958'
path_result = 'results/potjans_diesmann/'+id_result+'/'


# Llama a la función para obtener los archivos que comienzan con "spike_recorder"
archivos_spike_recorder = select_spike_recorder_files(path_result)
process_files_in_pairs(path_result, archivos_spike_recorder)





