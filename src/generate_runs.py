"""Hace el histograma
summary_
"""
import os
import warnings
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tools.particle_swarm_optimization as pso

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')
    n_trials, n_subjects = 1, 1

    ## Inicialización
    #pso.generate_first_population(folder_path, n_subjects)

    for trial in range(n_trials):
        for subject in range(n_subjects):
            for j in range(1):
            #trial, subject = 49, 10
            #if len(pso.get_result(folder_path, trial, subject)) == 0:
                os.system("python -m src.run_model_busse "+str('0')+" "+str('3'))

            #if len(pso.get_result(folder_path, trial, subject)) == 0:
            #    pso.save_imposed_result(folder_path, trial, subject, [0, 0, 0, 0, 10000])
        
        #if len(pso.get_subject(folder_path, trial+1, subject)) == 0 and trial < n_trials-1:
         #   pso.generate_next_iteration(folder_path, trial, n_subjects)