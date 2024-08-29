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

from utils import helpers

from assets.potjans_diesmann.sim_params import sim_dict # simulación

from assets.potjans_diesmann.stimulus_params1 import stim_dict1

from assets.potjans_diesmann.lateral_params import lateral_dict

from assets.potjans_diesmann.network_params import net_dict #para cada microcircuito es igual

import tools.particle_swarm_optimization as pso

from . import network_potjans_diesmann as network

parser = argparse.ArgumentParser()
parser.add_argument('gen', type=int)
parser.add_argument('id_s', type=int)

if __name__ == '__main__':
    args = parser.parse_args()
    
    folder_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/')
    subject_params = pso.get_subject(folder_path, args.gen, args.id_s)
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
    net_dict.update({'N_scaling': 0.1})
    net_dict.update({'K_scaling': 0.1})

    # Scaling thalamic neurons
    #stim_dict1['num_th_neurons'] = np.round((stim_dict1['num_th_neurons'] *
    #                                 net_dict['N_scaling'])).astype(int)
    stim_dict2 = stim_dict1.copy()
    stim_dict3 = stim_dict1.copy()
    stim_dict4 = stim_dict1.copy()

    # Lateral and vertical N & K scaling
    lateral_dict.update({'N_scaling': net_dict['N_scaling']})
    lateral_dict.update({'K_scaling': net_dict['K_scaling']})
    
    # Horizontal weights update
    new_conn_probs = pso.new_conn_probs(subject_params)
    lateral_dict.update({'conn_probs': new_conn_probs})
  
    # Simulation params
    sim_dutation = 1000.0
    sim_dict.update({'t_sim': sim_dutation})

    # Stimulation to MCC A
    stim_star = 250.0
    stim_duration = 750.0

    stim_dict1.update({'thalamic_input': True})
    stim_dict1.update({'th_start': stim_star})
    stim_dict1.update({'th_duration': stim_duration})
    stim_dict1.update({'th_rate': 15.0})

    # Stimulation to MCC B
    stim_star = 500.0
    stim_duration = 250.0

    stim_dict2.update({'thalamic_input': True})
    stim_dict2.update({'th_start': stim_star})
    stim_dict2.update({'th_duration': stim_duration})
    stim_dict2.update({'th_rate': 15.0})

    # Stimulation to MCC B 2
    stim_star = 750.0
    stim_duration = 250.0

    stim_dict3.update({'thalamic_input': True})
    stim_dict3.update({'th_start': stim_star})
    stim_dict3.update({'th_duration': stim_duration})
    stim_dict3.update({'th_rate': 22.0})


    ###############################################################################
    # Model type
    V1_B = True
    Lat_conn = True
    plot_hist = False
    

    ###############################################################################
    # Microcircuits V1 created
    print("---> Creating Microcircuits...")

    ###############################################################################
    # Create MCC A
    print("---> Creating networks V1_A...")
    #nest.rng_seed = randint(1, 1000)
    nest.rng_seed = 55
    rng_seeds.append(nest.rng_seed)
    net_A = network.Network(sim_dict, net_dict, stim_dict1)
    time_network_A = time.time()
    
    # Create all nodes
    net_A.create()
    time_create_A = time.time()

    # Connect all nodes
    net_A.connect()
    time_connect_A = time.time()

    ###############################################################################
    # Create MCC B
    if V1_B:
        print("---> Creating networks V1_B...")
        #nest.rng_seed = randint(1, 1000)
        nest.rng_seed = 56
        rng_seeds.append(nest.rng_seed)
        net_B = network.Network(sim_dict, net_dict, stim_dict2)
        time_network_B = time.time()

        # Create all nodes
        net_B.create()
        time_create_B = time.time()

        # Connect all nodes
        net_B.connect()
        time_connect_B = time.time()

        net_B.connect_other_input(stim_dict3)

    #conn = nest.GetConnections().get()

    ###############################################################################
    # Lateral connections
    if Lat_conn:
        print("---> Connecting networks laterally...")
        if V1_B:
            nest.rng_seed = 58
            net_A.connect_networks(net_B, lateral_dict)
            nest.rng_seed = 59
            net_B.connect_networks(net_A, lateral_dict)

    ###############################################################################
    # Simulation over MCC A
    print('---> Simulating...')
    nest.Prepare()
    nest.Cleanup()

    print('**********************************************')
    print('TRL: '+str(args.gen)+', SUJ : '+str(args.id_s) )
    print('**********************************************')
    net_A.simulate(sim_dict['t_sim'])
    time_simulate = time.time()

    ###############################################################################
    # Plot a spike raster of the simulated neurons and a box plot of the firing
    # rates for each population.
    # For visual purposes only, spikes 100 ms before and 100 ms after the thalamic
    # stimulus time are plotted here by default.
    # The computation of spike rates discards the presimulation time to exclude
    # initialization artifacts.
    print('---> Evaluating...')
    raster_plot_interval = np.array([sim_dict['t_presim'], sim_dict["t_sim"]])
    #firing_rates_interval0 = np.array([0, 500])
    #firing_rates_interval1 = np.array([500, 1000])
    #firing_rates_interval2 = np.array([1000, 1500])
    #firing_rates_interval3 = np.array([1500, 2000])

    all_pops = list(map(lambda pop: f"{pop}_A", net_dict['populations'])) + list(map(lambda pop: f"{pop}_B", net_dict['populations'])) 

    print('Interval to plot spikes: {} ms'.format(raster_plot_interval))
    if sim_dict.get('plot_raster', False):
        id_sim = sim_dict['data_path'].split("/")[-1]
        helpers.plot_raster(
            sim_dict['data_path'],
            'spike_recorder',
            raster_plot_interval[0],
            raster_plot_interval[1],
            net_dict['N_scaling'],
            all_pops,
            id_sim)

    #net_src.evaluate(raster_plot_interval, firing_rates_interval)
    time_evaluate = time.time()

    ###############################################################################
    # Histogramas de spikes and save performance
    data_path = sim_dict.get('data_path', None)
    pso.save_result(folder_path, data_path, args.gen, args.id_s)

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
    #plt.show()
