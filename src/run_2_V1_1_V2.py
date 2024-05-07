"""_summary_
"""
import time
import os
from random import randint
import json
import nest
import numpy as np

from utils import helpers

from assets.potjans_diesmann.sim_params import sim_dict # simulación

from assets.potjans_diesmann.stimulus_params import stim_dict
from assets.potjans_diesmann.stimulus_params2 import stim_dict as stim_dict2
from assets.potjans_diesmann.stimulus_params3 import stim_dict as stim_dict3

from assets.potjans_diesmann.lateral_params import lateral_dict
from assets.potjans_diesmann.feedforward_params import feedforward_dict
from assets.potjans_diesmann.feedback_params import feedback_dict

from assets.potjans_diesmann.network_params import net_dict #para cada microcircuito es igual

from . import network_potjans_diesmann as network

if __name__ == '__main__':

    time_start = time.time()

    nest.ResetKernel()
    nest.local_num_threads = sim_dict['local_num_threads']
    nest.resolution = sim_dict['sim_resolution']
    nest.rng_seed = sim_dict['rng_seed']
    nest.overwrite_files = sim_dict['overwrite_files']
    nest.print_time = sim_dict['print_time']
    
    if nest.Rank() == 0:
        print('RNG seed: {}'.format(
            nest.rng_seed))
        print('Total number of virtual processes: {}'.format(
            nest.total_num_virtual_procs))

    print('---------> Starting simulation...')
    # N and K scaling
    net_dict.update({'N_scaling': 0.05})
    net_dict.update({'K_scaling': 0.05})

    # Scaling thalamic neurons
    stim_dict['num_th_neurons'] = np.round((stim_dict['num_th_neurons'] *
                                     net_dict['N_scaling'])).astype(int)
    stim_dict2['num_th_neurons'] = np.round((stim_dict2['num_th_neurons'] *
                                     net_dict['N_scaling'])).astype(int)
    stim_dict3['num_th_neurons'] = np.round((stim_dict3['num_th_neurons'] *
                                     net_dict['N_scaling'])).astype(int)

    # N & K scaling
    lateral_dict.update({'N_scaling': net_dict['N_scaling']})
    lateral_dict.update({'K_scaling': net_dict['K_scaling']})
    feedforward_dict.update({'N_scaling': net_dict['N_scaling']})
    feedforward_dict.update({'K_scaling': net_dict['K_scaling']})
    feedback_dict.update({'N_scaling': net_dict['N_scaling']})
    feedback_dict.update({'K_scaling': net_dict['K_scaling']})

    # toy example
    Cte_value = True
    if Cte_value:
        sim_dict.update({'t_sim': 500.0})
                
        stim_dict.update({'thalamic_input': True})
        stim_dict.update({'th_start': 200.0})
        stim_dict.update({'th_duration': 200.0})
        stim_dict.update({'th_rate': 20.0})

        stim_dict2.update({'thalamic_input': True})
        stim_dict2.update({'th_start': 200.0})
        stim_dict2.update({'th_duration': 200.0})
        stim_dict2.update({'th_rate': 10.0})

        stim_dict3.update({'thalamic_input': False})
        stim_dict3.update({'th_start': 200.0})
        stim_dict3.update({'th_duration': 500.0})
        stim_dict3.update({'th_rate': 10.0})
    
    data_path = sim_dict.get('data_path', None)
    rng_seeds = []

    # MCC A
    # Create network
    print("---> Creating A network...")
    nest.rng_seed = randint(1, 1000)
    rng_seeds.append(nest.rng_seed)
    net_A = network.Network(sim_dict, net_dict, stim_dict)
    time_network_A = time.time()
    # Create all nodes
    net_A.create()
    time_create_A = time.time()
    # Connect all nodes
    print("---> Connecting source network...")
    net_A.connect()
    time_connect_A = time.time()

    
    # MCC B
    # Create network
    print("---> Creating B network...")
    nest.rng_seed = randint(1, 1000)
    rng_seeds.append(nest.rng_seed)
    net_B = network.Network(sim_dict, net_dict, stim_dict2)
    time_network_B = time.time()
    # Create all nodes
    net_B.create()
    time_create_B = time.time()
    # Connect all nodes
    print("---> Connecting target network...")
    net_B.connect()
    time_connect_B = time.time()

    # MCC C
    # Create network
    print("---> Creating C network...")
    nest.rng_seed = randint(1, 1000)
    rng_seeds.append(nest.rng_seed)
    net_C = network.Network(sim_dict, net_dict, stim_dict3)
    time_network_C = time.time()
    # Create all nodes
    net_C.create()
    time_create_C = time.time()
    # Connect all nodes
    print("---> Connecting target n20etwork...")
    net_C.connect()
    time_connect_C = time.time()

    with open(os.path.join(data_path, 'seeds.json'), 'w') as file:
        json.dump(rng_seeds, file)
    #conn = nest.GetConnections().get()
    
    print("---> Connecting NETWORKS...")
    net_A.connect_networks(net_B, lateral_dict)
    net_B.connect_networks(net_A, lateral_dict)

    net_A.connect_networks(net_C, feedforward_dict)
    net_B.connect_networks(net_C, feedforward_dict)

    net_C.connect_networks(net_B, feedback_dict)
    net_C.connect_networks(net_A, feedback_dict)

    nest.Prepare()
    nest.Cleanup()

    print('---> Simulating...')
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
    raster_plot_interval = np.array([sim_dict['t_presim']+100, sim_dict["t_sim"]])
    firing_rates_interval = np.array([sim_dict['t_presim']+100, sim_dict["t_sim"]])

    all_pops = list(map(lambda pop: f"{pop}_A", net_dict['populations'])) + list(map(lambda pop: f"{pop}_B", net_dict['populations'])) + list(map(lambda pop: f"{pop}_C", net_dict['populations']))

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
        
    print('Interval to compute firing rates: {} ms'.format(firing_rates_interval))
    if sim_dict.get("plot_firing_rates", False):
        helpers.firing_rates(
            sim_dict['data_path'],
            'spike_recorder',
            firing_rates_interval[0],
            firing_rates_interval[1])
        helpers.boxplot(sim_dict["data_path"], all_pops)

    #net_src.evaluate(raster_plot_interval, firing_rates_interval)
    time_evaluate = time.time()

    ###############################################################################
    # Histogramas de spikes
    import tools.histogram_single_microcircuit as hist_spikes
    data_path = sim_dict.get('data_path', None)
    hist_spikes.apliccation_metrics(data_path)

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
