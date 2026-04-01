"""
run_experiment.py
Script unificado para ejecutar simulaciones de microcircuitos corticales.
Reemplaza los múltiples archivos run_model_*.py
"""
import argparse
import time
import nest
from random import randint

# Importaciones base (asumiendo tu estructura actual en assets)
# Nota: A futuro, esto es lo que reemplazarás por un lector de YAML/JSON
from assets.potjans_diesmann.sim_params import sim_dict
from assets.potjans_diesmann.stimulus_params import stim_dict

from assets.potjans_diesmann.network_params import net_dict, net_dict_v2
from assets.potjans_diesmann.lateral_params import lateral_dict_near, lateral_dict_far

from assets.potjans_diesmann.feedforward_params import feedforward_dict 
from assets.potjans_diesmann.feedback_params import feedback_dict

from src.network_potjans_diesmann import Network

import tools.peristimulus_time_histogram as psth


def connect_columns_lat(column_a, column_b, conn_dict):
    column_a.connect_networks(column_b, conn_dict)
    column_b.connect_networks(column_a, conn_dict)


def main():
    # Definir los argumentos que aceptará la terminal
    parser = argparse.ArgumentParser(description="Simulador unificado de NEST para Potjans-Diesmann")
    
    # Parámetros numéricos
    parser.add_argument('--ns', type=float, default=1.0, help="N_scaling (Escalado de neuronas)")
    parser.add_argument('--ks', type=float, default=1.0, help="K_scaling (Escalado de conexiones)")
    parser.add_argument('--stim_rate', type=float, default=200.0, help="Tasa del estímulo talámico (Hz)")
    parser.add_argument('--stim_rate_ecrf', type=float, default=0.0, help="Tasa del estímulo talámico (Hz) ecrf")
    
    # Flags para activar/desactivar microcircuitos (si pones --v1_b en la terminal, es True)
    parser.add_argument('--v1', action='store_true', help="Activa la población V1")
    parser.add_argument('--v2', action='store_true', help="Activa la población V2")
    
    # Flags para conexiones
    parser.add_argument('--lat', action='store_true', help="Conecta V1_A con V1_B (Lateral)")
    parser.add_argument('--ff', action='store_true', help="Conecta V1_A con V2 (Feedforward)")
    parser.add_argument('--fb', action='store_true', help="Conecta V2 con V1_A (Feedback)")
    
    args = parser.parse_args()

    print("--- Configurando Experimento ---")
    
    # Inicializar NEST y limpiar memoria
    nest.ResetKernel()
    nest.local_num_threads = sim_dict['local_num_threads']
    nest.resolution        = sim_dict['sim_resolution']
    nest.overwrite_files   = sim_dict['overwrite_files']
    nest.print_time        = sim_dict['print_time']

    # Actualizar los diccionarios con los argumentos que entraron por consola
    diccionarios = (
        net_dict, 
        net_dict_v2, 
        lateral_dict_near, 
        lateral_dict_far, 
        feedback_dict, 
        feedforward_dict
    )

    for d in diccionarios:
        d['N_scaling'] = args.ns
        d['K_scaling'] = args.ks

    stim_dict['th_rate'] = args.stim_rate
    columnas = {}

    # Crear el microcircuito principal (siempre se crea)
    print(f"Creando V1_A (N_scaling: {args.ns}, K_scaling: {args.ks})...")
    nest.rng_seed = randint(1, 1000)
    columnas['V1_A'] = Network(sim_dict, net_dict, stim_dict)
    columnas['V1_A'].create()
    columnas['V1_A'].connect()

    # Crear microcircuitos adicionales solo si se solicitan
    if args.v1:
        stim_dict['th_rate'] = 0.0
        V1 = ['V1_B', 'V1_C', 'V1_D']
        for v1 in V1:
            print(f"Creando {v1}...")
            nest.rng_seed = randint(1, 1000)
            if v1 == 'V1_D' and args.stim_rate_ecrf != 0.0:
                    stim_dict['th_rate'] = args.stim_rate_ecrf
            columnas[v1] = Network(sim_dict, net_dict, stim_dict)
            columnas[v1].create()
            columnas[v1].connect()
        
    if args.v2:
        stim_dict['thalamic_input'] = False
        stim_dict['num_th_neurons'] = 0.0
        V2 = ['V2_A', 'V2_B']
        for v2 in V2:
            print(f"Creando {v2}...")
            nest.rng_seed = randint(1, 1000)
            columnas[v2] = Network(sim_dict, net_dict_v2, stim_dict)
            columnas[v2].create()
            columnas[v2].connect()

    # Conectar topología a gran escala (Macro-conectividad)
    if args.lat:
        if args.v1:
            print("-> Conectando Lateral en V1")
            connect_columns_lat(columnas['V1_A'], columnas['V1_B'], lateral_dict_near)
            connect_columns_lat(columnas['V1_C'], columnas['V1_D'], lateral_dict_near)

            connect_columns_lat(columnas['V1_A'], columnas['V1_C'], lateral_dict_far)
            connect_columns_lat(columnas['V1_A'], columnas['V1_D'], lateral_dict_far)       
            connect_columns_lat(columnas['V1_B'], columnas['V1_C'], lateral_dict_far)
            connect_columns_lat(columnas['V1_B'], columnas['V1_D'], lateral_dict_far)

        if args.v2:
            print("-> Conectando Lateral en V2")
            connect_columns_lat(columnas['V2_A'], columnas['V2_B'], lateral_dict_far)
            
    if args.ff and args.v2:
        print("-> Conectando Feedforward")
        columnas['V1_A'].connect_networks(columnas['V2_A'], feedforward_dict)
        columnas['V1_B'].connect_networks(columnas['V2_A'], feedforward_dict)

        columnas['V1_C'].connect_networks(columnas['V2_B'], feedforward_dict)
        columnas['V1_D'].connect_networks(columnas['V2_B'], feedforward_dict)

    if args.fb and args.v2:
        print("-> Conectando Feedback")
        columnas['V2_A'].connect_networks(columnas['V1_A'], feedback_dict)
        columnas['V2_A'].connect_networks(columnas['V1_B'], feedback_dict)

        columnas['V2_B'].connect_networks(columnas['V1_C'], feedback_dict)
        columnas['V2_B'].connect_networks(columnas['V1_D'], feedback_dict)

    # Simular
    t_sim = sim_dict.get("t_sim", 1000.0)
    print(f"--- Iniciando Simulación ({t_sim} ms) ---")
    tic = time.time()
    
    nest.Simulate(t_sim)
    
    toc = time.time()
    print(f"--- Simulación Finalizada en {toc - tic:.2f} segundos ---")
    
    # Aquí puedes agregar el código para guardar los spikes o calcular el LFP

if __name__ == '__main__':
    main()