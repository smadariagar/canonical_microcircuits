import os
import warnings
import pandas as pd
import numpy as np
import math
import argparse


import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
from matplotlib.ticker import MaxNLocator
import seaborn as sns

import tools.particle_swarm_optimization as pso
import tools.particle_swarm_optimization_plot as pso_plt
import tools.peristimulus_time_histogram as psth
import tools.metrics as met

parser = argparse.ArgumentParser()
parser.add_argument('dir')

if __name__ == '__main__':
    args = parser.parse_args()
    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')

    ruta_completa = os.path.join(folder_path, args.dir)
        
    print("Accediendo a:", args.dir)
    
    #try:
    archivos_spike_recorder = met.select_spike_recorder_files(ruta_completa)
    # print(archivos_spike_recorder)
    # archivos_spike_recorder.sort()
    met.process_files_in_pairs(ruta_completa, archivos_spike_recorder)
