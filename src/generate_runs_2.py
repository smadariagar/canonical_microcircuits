"""Hace el histograma
summary_
"""
import os
import warnings

import tools.particle_swarm_optimization as pso
import numpy as np

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')

    for j in range(1):
        for k in range(10):
            os.system("python -m src.run_model_busse_params "+str(j)+" "+str(k))
