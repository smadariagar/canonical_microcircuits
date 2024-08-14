"""Hace el histograma
summary_
"""
import os
import warnings
import pandas as pd
import numpy as np

import tools.particle_swarm_optimization as pso

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')

    ## Inicialización
    # creación de data inicial
    # Población inicial de 10 ind
    # las conexiones serán desde L23E, l5E y L6E a todas los grupos 3x8
    #pso.generate_first_population(folder_path, 10)
    if False:
        trial, subject = 0, 0
        for i in range(10):
    #    for subject in range(10):
            os.system("python -m src.run_model_busse "+str(trial)+" "+str(subject))

    pso.plot_params(folder_path, 9)
    pso.plot_performance(folder_path, -1)
        #pso.generate_next_iteration(folder_path, trial)
    plt.show()