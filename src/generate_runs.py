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
    n_trials, n_subjects = 1, 10
    params = 8

    ## Inicialización
    # if not os.path.exists(os.path.join(folder_path, 'swarm.csv')):
    #     print('New swarm data')
    pso.generate_first_population(folder_path, n_subjects, params)

    for trial in range(n_trials):
        for subject in range(n_subjects):

            if len(pso.get_result(folder_path, trial, subject)) == 0:
                #os.system("python -m src.run_model_busse "+str(trial)+" "+str(subject))
                os.system("python -m src.run_model_busse_params "+str(trial)+" "+str(subject))

            if len(pso.get_result(folder_path, trial, subject)) == 0:
                pso.save_imposed_result(folder_path, trial, subject, [0, 0, 0, 0, 10000])
        
        if len(pso.get_subject(folder_path, trial+1, subject, params)) == 0 and trial < n_trials-1:
            pso.generate_next_iteration(folder_path, trial, n_subjects, params)
