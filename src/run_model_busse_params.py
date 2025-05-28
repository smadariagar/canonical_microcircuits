# -*- coding: utf-8 -*-
#
# run_model.py
#
# Este código debería correr todas las variables de mi modelo.
# Todo el modelo está construido sobre NEST
#
# Copyright (C) 2004 The NEST Initiative
#
# NEST is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# NEST is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with NEST.  If not, see <http://www.gnu.org/licenses/>.

"""Run Simulation
-----------------------------------------

Este script corre el modelo de corteza visual, con módulos de microcircuito tanto en V1 como en V2.

"""

###############################################################################
# Import the necessary modules and start the time measurements.
import time
import os

import json
import argparse
from random import randint

import nest
import numpy as np
import pandas as pd

from utils import helpers

from assets.potjans_diesmann.sim_params import sim_dict # simulación

from assets.potjans_diesmann.stimulus_params1 import stim_dict as stim_dict_A

from assets.potjans_diesmann.lateral_params import lateral_dict
from assets.potjans_diesmann.lateral_params2 import lateral_dict as lateral_dict2

from assets.potjans_diesmann.feedforward_params import feedforward_dict as FF_dict
from assets.potjans_diesmann.feedback_params import feedback_dict as FB_dict

from assets.potjans_diesmann.network_params import net_dict #para cada microcircuito es igual
from assets.potjans_diesmann.network_params_V2 import net_dict_v2

import tools.particle_swarm_optimization as pso
import tools.peristimulus_time_histogram as psth

from . import network_potjans_diesmann as network


parser = argparse.ArgumentParser()
parser.add_argument('gen', type=int)
parser.add_argument('id_s', type=int)

if __name__ == '__main__':
    args = parser.parse_args()
    
    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')
    #subject_params = pso.get_subject(folder_path, args.gen, args.id_s, 8)
    time_start = time.time()

    nest.ResetKernel()
    nest.local_num_threads = sim_dict['local_num_threads']
    nest.resolution        = sim_dict['sim_resolution']
    nest.rng_seed          = sim_dict['rng_seed']
    nest.overwrite_files   = sim_dict['overwrite_files']
    nest.print_time        = sim_dict['print_time']

    if nest.Rank() == 0:
        print('RNG seed: {}'.format(
            nest.rng_seed))
        print('Total number of virtual processes: {}'.format(
            nest.total_num_virtual_procs))

    data_path = sim_dict.get('data_path', None)
    rng_seeds = []


    ###############################################################################
    # Modelo de 2 MCC en V1
    print('---------> Creating the model...')

    # N & K scaling
    ns = 1#(args.gen+1)/10
    ks = 1#(args.gen+1)/10

    net_dict.update({'N_scaling': ns})
    net_dict.update({'K_scaling': ks})

    net_dict_v2.update({'N_scaling': ns})
    net_dict_v2.update({'K_scaling': ks})

    # Lateral and vertical N & K scaling
    lateral_dict.update({'N_scaling': ns})
    lateral_dict.update({'K_scaling': ks})
    
    lateral_dict2.update({'N_scaling': ns})
    lateral_dict2.update({'K_scaling': ks})

    FF_dict.update({'N_scaling': ns})
    FF_dict.update({'K_scaling': ks})
    
    FB_dict.update({'N_scaling': ns})
    FB_dict.update({'K_scaling': ks})

    # Horizontal weights update
    #new_conn_probs = pso.new_conn_probs_alternative(subject_params)
    #FB_dict.update({'conn_probs': new_conn_probs})
    
    # Simulation params
    sim_dutation = 3000.0 
    sim_dict.update({'t_sim': sim_dutation})

    #stim_dict_A.update({'num_th_neurons': 0})

    # Generación de estímulos
    stim_dict_B = stim_dict_A.copy() 
    stim_dict_C = stim_dict_A.copy()
    stim_dict_D = stim_dict_A.copy() 
    stim_dict_V2 = stim_dict_A.copy()


    # Stimulation to MCC A
    stim_star = 1000.0 
    stim_duration = 2000.0

    stim_dict_A.update({'thalamic_input': True})
    stim_dict_A.update({'th_start': stim_star})
    stim_dict_A.update({'th_duration': stim_duration})

    stim_dict_A.update({'th_rate': 200.0})

    # Stimulation to MCC B
    stim_star = 1000.0 
    stim_duration = 1500.0
    
    stim_dict_B.update({'thalamic_input': False})
    stim_dict_B.update({'th_start': stim_star})
    stim_dict_B.update({'th_duration': stim_duration})
    stim_dict_B.update({'th_rate': 200.0})

    #stim_dict_B.update({'num_th_neurons': 200})


    # Stimulation to MCC C
    stim_star = 2000.0 
    stim_duration = 1000.0

    # if args.gen == 0:
    #     TR = 200.0
    # elif args.gen == 1:
    #     TR = 100.0
    # # elif args.gen == 2:
    # #     TR = 300.0


    stim_dict_C.update({'thalamic_input': True})
    stim_dict_C.update({'th_start': stim_star})
    stim_dict_C.update({'th_duration': stim_duration})
    stim_dict_C.update({'th_rate': 300.0})

    # Stimulation to MCC D
    stim_star = 1500.0 
    stim_duration = 1000.0

    stim_dict_D.update({'thalamic_input': False})
    stim_dict_D.update({'th_start': stim_star})
    stim_dict_D.update({'th_duration': stim_duration})
    stim_dict_D.update({'th_rate': 200.0})

    #stim_dict_D.update({'num_th_neurons': 200})


    ###############################################################################
    # Model type
    V1 = False
    # if args.gen == 0:
    #     V2, V22 = False, False
    # if args.gen == 1:
    #     V2, V22 = True, False
    # if args.gen == 2:
    #     V2, V22 = True, True
    Lat_conn, Strg_conn = False, False
    
    V2, V22 = False, False
    FF_conn, FB_conn = False, False


    ###############################################################################
    # Microcircuits V1 created

    print("---> Creating Microcircuits...")
    #net_dict.update({'K_ext': np.array([1600, 1500, 2100, 1900, 2000, 1900, 2900, 2100])})
    #net_dict.update({'K_ext': np.array([1500, 1500, 2100, 1900, 1950, 1900, 2900, 2100])}) #con v2

    ###############################################################################
    # Create MCC A
    print("---> Creating networks V1_A...")
    nest.rng_seed = randint(1, 1000)
    #nest.rng_seed = 55
    rng_seeds.append(nest.rng_seed)
    net_A = network.Network(sim_dict, net_dict, stim_dict_A)
    time_network_A = time.time()
    
    # Create all nodes
    net_A.create()
    time_create_A = time.time()

    # Connect all nodes
    net_A.connect()
    time_connect_A = time.time()
    all_pops = list(map(lambda pop: f"{pop}", net_dict['populations']))


    ###############################################################################
    # Create V!
    if V1:
    ###############################################################################
    # Create MCC B    
        print("---> Creating networks V1_B...")
        nest.rng_seed = randint(1, 1000)
        #nest.rng_seed = 56
        rng_seeds.append(nest.rng_seed)
        net_B = network.Network(sim_dict, net_dict, stim_dict_B)

        # Create all nodes
        net_B.create()

        # Connect all nodes
        net_B.connect()
        all_pops = all_pops + list(map(lambda pop: f"{pop}", net_dict['populations'])) 


    ###############################################################################
    # Create MCC C
        print("---> Creating networks V1_C...")
        nest.rng_seed = randint(1, 1000)
        #nest.rng_seed = 56
        rng_seeds.append(nest.rng_seed)
        net_C = network.Network(sim_dict, net_dict, stim_dict_C)

        # Create all nodes
        net_C.create()

        # Connect all nodes
        net_C.connect()
        all_pops = all_pops + list(map(lambda pop: f"{pop}", net_dict['populations'])) 


    ###############################################################################
    # Create MCC D
        print("---> Creating networks V1_D...")
        nest.rng_seed = randint(1, 1000)
        #nest.rng_seed = 56
        rng_seeds.append(nest.rng_seed)
        net_D = network.Network(sim_dict, net_dict, stim_dict_D)
        
        # Create all nodes
        net_D.create()

        # Connect all nodes
        net_D.connect()
        all_pops = all_pops + list(map(lambda pop: f"{pop}", net_dict['populations']))

     
    ###############################################################################
    # Lateral connections
    if V1:
        print("---> Connecting networks laterally...")
        if Lat_conn:
            nest.rng_seed = randint(1, 1000)
            net_A.connect_networks(net_B, lateral_dict)
            nest.rng_seed = randint(1, 1000)
            net_B.connect_networks(net_A, lateral_dict)
            
            nest.rng_seed = randint(1, 1000)
            net_C.connect_networks(net_D, lateral_dict)
            nest.rng_seed = randint(1, 1000)
            net_D.connect_networks(net_C, lateral_dict)

            nest.rng_seed = randint(1, 1000)
            net_A.connect_networks(net_C, lateral_dict2)
            nest.rng_seed = randint(1, 1000)
            net_C.connect_networks(net_A, lateral_dict2)
            nest.rng_seed = randint(1, 1000)
            net_B.connect_networks(net_D, lateral_dict2)                    
            nest.rng_seed = randint(1, 1000)
            net_D.connect_networks(net_B, lateral_dict2)

            if Strg_conn:
                nest.rng_seed = randint(1, 1000)
                net_A.connect_networks(net_D, lateral_dict)
                nest.rng_seed = randint(1, 1000)
                net_D.connect_networks(net_A, lateral_dict)

                nest.rng_seed = randint(1, 1000)
                net_B.connect_networks(net_C, lateral_dict)
                nest.rng_seed = randint(1, 1000)
                net_C.connect_networks(net_B, lateral_dict)

            else:
                nest.rng_seed = randint(1, 1000)
                net_A.connect_networks(net_D, lateral_dict2)
                nest.rng_seed = randint(1, 1000)
                net_D.connect_networks(net_A, lateral_dict2)

                nest.rng_seed = randint(1, 1000)
                net_B.connect_networks(net_C, lateral_dict2)
                nest.rng_seed = randint(1, 1000)
                net_C.connect_networks(net_B, lateral_dict2)



    ###############################################################################
    # Create MCC v2
    if V2:
        #net_dict.update({'K_ext': np.array([1600, 1500, 2100, 1900, 2000, 1900, 2900, 2100])})
        ####net_dict.update({'K_ext': np.array([1700, 1500, 1550, 1420, 1900, 1900, 2800, 2100])})
        
        #net_dict.update({'full_num_neurons': np.array([20683, 5834, 21915, 5479, 4850, 1065, 14395, 2948])})
        #net_dict.update({'full_num_neurons': np.array([20683, 5834, 20915, 5279, 4850, 1065, 14395, 2948])})
        ####net_dict.update({'full_num_neurons': np.array([22051,  6219, 11421, 2855, 4461, 979,  13966, 2859])})
        #net_dict.update({'full_num_neurons': np.array([22051,  6219, 15421, 3855, 4461, 979,  13966, 2859])})

        stim_dict_V2.update({'num_th_neurons': 0}) 
        print("---> Creating networks V2...")
        nest.rng_seed = randint(1, 1000)
        #nest.rng_seed = 56
        rng_seeds.append(nest.rng_seed)
        net_V2 = network.Network(sim_dict, net_dict_v2, stim_dict_V2)

        # Create all nodes
        net_V2.create()

        # Connect all nodes
        net_V2.connect()

        #net_V2.connect_other_input(stim_dict3_v2)
        all_pops = all_pops + list(map(lambda pop: f"{pop}", net_dict_v2['populations'])) 
      
    if V22:
        nest.rng_seed = randint(1, 1000)
        #nest.rng_seed = 56
        rng_seeds.append(nest.rng_seed)
        net_V22 = network.Network(sim_dict, net_dict_v2, stim_dict_V2)

        # Create all nodes
        net_V22.create()

        # Connect all nodes
        net_V22.connect()

        #net_V2.connect_other_input(stim_dict3_v2)
        all_pops = all_pops + list(map(lambda pop: f"{pop}", net_dict_v2['populations'])) 


    ###############################################################################
    # Vertica connections
    #feedforward
    if V2:
        if FF_conn:
            print("---> Connecting networks vertically...")
            nest.rng_seed = randint(1, 1000)
            net_A.connect_networks(net_V2, FF_dict)
            nest.rng_seed = randint(1, 1000)
            net_B.connect_networks(net_V2, FF_dict)

            if V22:
                nest.rng_seed = randint(1, 1000)
                net_C.connect_networks(net_V22, FF_dict)
                nest.rng_seed = randint(1, 1000)
                net_D.connect_networks(net_V22, FF_dict)

            else:
                nest.rng_seed = randint(1, 1000)
                net_C.connect_networks(net_V2, FF_dict)
                nest.rng_seed = randint(1, 1000)
                net_D.connect_networks(net_V2, FF_dict)

        #feedback
        if FB_conn:
            nest.rng_seed = randint(1, 1000)
            net_V2.connect_networks(net_A, FB_dict)
            nest.rng_seed = randint(1, 1000)
            net_V2.connect_networks(net_B, FB_dict)

            if V22:
                nest.rng_seed = randint(1, 1000)
                net_V22.connect_networks(net_C, FB_dict)
                nest.rng_seed = randint(1, 1000)
                net_V22.connect_networks(net_D, FB_dict)
                
            else:
                nest.rng_seed = randint(1, 1000)
                net_V2.connect_networks(net_C, FB_dict)
                nest.rng_seed = randint(1, 1000)
                net_V2.connect_networks(net_D, FB_dict)


        if V22:
            nest.rng_seed = randint(1, 1000)
            net_V2.connect_networks(net_V22, lateral_dict2)
            nest.rng_seed = randint(1, 1000)
            net_V22.connect_networks(net_V2, lateral_dict2)

    
    ###############################################################################
    # Simulation over MCC A
    print('---> Simulating...')
    nest.Prepare()
    nest.Cleanup()
    nest.rng_seed = randint(1, 1000)

    print('**********************************************')
    print('TRL: '+str(args.gen)+', SUJ : '+str(args.id_s) )
    print('**********************************************')
    net_A.simulate(sim_dict['t_sim'])
    time_simulate = time.time()

    ###############################################################################
    # Save dict
    pd.Series(net_dict).to_json(os.path.join(data_path,'net_params.json'))
    pd.Series(net_dict_v2).to_json(os.path.join(data_path,'net_v2_params.json'))
    pd.Series(lateral_dict).to_json(os.path.join(data_path,'lat_conn_params.json'))
    pd.Series(lateral_dict2).to_json(os.path.join(data_path,'lat_conn_far_params.json'))
    pd.Series(FF_dict).to_json(os.path.join(data_path,'ff_conn_params.json'))
    pd.Series(FB_dict).to_json(os.path.join(data_path,'fb_conn_params.json'))
    

    ###############################################################################
    # Plot a spike raster of the simulated neurons and a box plot of the firing
    # rates for each population.
    # For visual purposes only, spikes 100 ms before and 100 ms after the thalamic
    # stimulus time are plotted here by default.
    # The computation of spike rates discards the presimulation time to exclude
    # initialization artifacts.
    print('---> Evaluating...')
    raster_plot_interval = np.array([0, sim_dict["t_sim"]])
    firing_rates_interval = np.array([0, sim_dict["t_sim"]])

    #firing_rates_interval0 = np.array([0, 500])
    #firing_rates_interval1 = np.array([500, 1000])
    #firing_rates_interval2 = np.array([1000, 1500])
    #firing_rates_interval3 = np.array([1500, 2000])

    print('Interval to plot spikes: {} ms'.format(raster_plot_interval))
    if False:
        id_sim = sim_dict['data_path'].split("/")[-1]
        helpers.plot_raster(
            sim_dict['data_path'],
            'spike_recorder',
            raster_plot_interval[0],
            raster_plot_interval[1],
            net_dict['N_scaling'],
            all_pops,
            id_sim)

    names = ['CMC V1 ( l )', 'CMC V1 ( \\ )', 'CMC V1 ( - )', 'CMC V1 ( / )', 'CMC V2']#, 'CMC V22']

    print('Interval to compute firing rates: {} ms'.format(firing_rates_interval))
    if False:
        helpers.firing_rates(
            sim_dict['data_path'],
            'spike_recorder',
            firing_rates_interval[0],
            firing_rates_interval[1])
        helpers.boxplot(sim_dict['data_path'], all_pops, 'firing_rate_',  False, True, names)

    #net_src.evaluate(raster_plot_interval, firing_rates_interval)
    time_evaluate = time.time()


    ###############################################################################
    # Generate metrics
    # l_bin = 25
    # data_path = sim_dict.get('data_path', None)
    # psth.PSTH_data(data_path, net_dict['N_scaling'], sim_dict['t_sim'], l_bin)
    # psth.PSTH_plot_tog(data_path, sim_dict['t_sim'], l_bin)


    ###############################################################################
    # Histogramas de spikes and save performance
    #psth.PSTH_data(data_path, net_dict['N_scaling'], sim_dict['t_sim'], 500)
    #pso.save_result(folder_path, data_path, args.gen, args.id_s, net_A.num_neurons[0])
    #activity = psth.get_data(data_path, sim_dict['t_sim'], 500, '2/3a', 'exc')
    #pso.save_imposed_result(folder_path, args.gen, args.id_s, activity)


    ###############################################################################
    # Saving seeds
    with open(os.path.join(data_path, 'seeds.json'), 'w') as file:
        json.dump(rng_seeds, file)


    ###############################################################################
    # Summarize time measurements. Rank 0 usually takes longest because of the
    # data evaluation and print calls.
    print(
        '\nTimes of Rank {}:\n'.format(
            nest.Rank()) +
        '  Total time:          {:.3f} s\n'.format(
            time_evaluate -
            time_start) +
        '  Time to initialize:  {:.3f} s\n'.format(
            time_network_A -
            time_start) +
        '  Time to create:      {:.3f} s\n'.format(
            time_create_A -
            time_network_A) +
        '  Time to connect:     {:.3f} s\n'.format(
            time_connect_A -
            time_create_A) +
        '  Time to presimulate: {:.3f} s\n'.format(
            time_simulate -
            time_connect_A) +
        '  Time to simulate:    {:.3f} s\n'.format(
            time_simulate -
            time_connect_A) +
        '  Time to evaluate:    {:.3f} s\n'.format(
            time_evaluate -
            time_simulate))
    
