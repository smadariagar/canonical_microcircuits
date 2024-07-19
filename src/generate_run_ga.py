"""Hace el histograma
summary_
"""
import os
import warnings
import numpy as np

import tools.genetic_algorithm as gen_alg

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')

    ## Inicialización
    # creación de data inicial
    # Población inicial de 10 ind
    # las conexiones serán desde L23E, l5E y L6E a todas los grupos 3x8
    
    #gen_alg.generate_first_generation(folder_path, 10)
    #gen_alg.sort_best_performance(folder_path)
    ## Simulación N-ésima generación
    for generation in range(15,20):
    #generation = 0
        gen_alg.generate_next_generation(folder_path, generation-1)

        for i in range(10):

            os.system("python -m src.run_model_busse_ga "+str(generation)+" "+str(i))

        ## Generación nueva generación (parámetros)
        ## Seleción mejores

        
    #os.system("python -m src.generate_hist_folders")
    #gen_alg.plot_generation(folder_path,0)
    #gen_alg.sort_best_performance(folder_path)