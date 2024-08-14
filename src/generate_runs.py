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
   
    trial, subject = 0, 0
    n_trials = 50
    for trial in range(n_trials):
        for subject in range(10):

            if len(pso.get_result(folder_path, trial, subject)) == 0:
                os.system("python -m src.run_model_busse "+str(trial)+" "+str(subject))

            if len(pso.get_result(folder_path, trial, subject)) == 0:
                pso.save_imposed_result(folder_path, trial, subject, [0, 0, 0, 0])
        
        if len(pso.get_subject(folder_path, trial+1, subject)) == 0 & trial < n_trials-2:
            pso.generate_next_iteration(folder_path, trial)