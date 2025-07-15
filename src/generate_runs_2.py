"""Hace el histograma
summary_
"""
import os
import warnings
import pandas as pd
import numpy as np
import math

import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm, Normalize
from matplotlib.ticker import MaxNLocator
import seaborn as sns

import tools.particle_swarm_optimization as pso
import tools.particle_swarm_optimization_plot as pso_plt
import tools.peristimulus_time_histogram as psth

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')

    # for j in range(7):
    #     for k in range(1):
    #         os.system("python -m src.run_model_busse_params "+str(j)+" "+str(k))


    carpetas = [nombre for nombre in os.listdir(folder_path)
            if os.path.isdir(os.path.join(folder_path, nombre))]
    for carpeta in carpetas:
       
        os.system("python -m src.lfp "+carpeta)