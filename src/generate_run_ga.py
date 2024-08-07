"""Hace el histograma
summary_
"""
import os
import warnings
import pandas as pd
import numpy as np

import tools.genetic_algorithm as gen_alg

warnings.filterwarnings("ignore")

if __name__ == '__main__':

    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')

    gen_alg.generate_first_generation(folder_path, 10)
    os.system("python -m src.run_model_busse_ga "+str(0)+" "+str(0))

    ## Inicialización
    # creación de data inicial
    # Población inicial de 10 ind
    # las conexiones serán desde L23E, l5E y L6E a todas los grupos 3x8
    """ gen_alg.generate_first_generation(folder_path, 10)
    #gen_alg.sort_best_performance(folder_path)

    ## Simulación N-ésima generación
    for gen in range(20):

        for suj in range(10):

            if len(gen_alg.get_performance(folder_path, gen, suj)) == 0:
                os.system("python -m src.run_model_busse_ga "+str(gen)+" "+str(suj))

            if len(gen_alg.get_performance(folder_path, gen, suj)) == 0:
                # convert array into dataframe 
                df = pd.DataFrame([[gen, suj, 10000, 10001, 10002, 10003]]) 
                
                # save the dataframe as a csv file 
                df.to_csv(os.path.join(folder_path, 'performance.csv'), mode='a', index=False, header=False)

            print('****** Simulation generation '+str(gen)+' suj '+str(suj)+' is finished ******')
    
        ## Generación nueva generación (parámetros)
        ## Seleción mejores
        if gen < 19 and len(gen_alg.get_subject(folder_path, gen+1, 0)) == 0:
                gen_alg.generate_next_generation(folder_path, gen)

        print('****** Generation '+str(gen)+' is finished ******')

    ## Find the best of all
    gen_alg.sort_best_performance(folder_path)
    #gen_alg.plot_performance(folder_path) """

    ## brain in a dish son todos distincas conexiones -> puede haber otra solución 

