import nest
import time
import numpy as np
import matplotlib.pyplot as plt

from assets.potjans_diesmann.stimulus_params import stim_dict
from assets.potjans_diesmann.stimulus_params2 import stim_dict as stim_dict2
from assets.potjans_diesmann.stimulus_params3 import stim_dict as stim_dict3
from assets.potjans_diesmann.network_params import net_dict
from assets.potjans_diesmann.sim_params import sim_dict
from assets.potjans_diesmann.lateral_params import lateral_dict
from . import network_potjans_diesmann as network

from utils import helpers

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

    # Create network A
    print("---> Creating A network...")
    net_A = network.Network(sim_dict, net_dict, stim_dict)
    time_network_A = time.time()
    # Create all nodes
    net_A.create()
    time_create_A = time.time()
    # Connect all nodes
    print("---> Connecting A network...")
    net_A.connect()
    time_connect_A = time.time()

    # Create network B
    print("---> Creating B network...")
    net_B = network.Network(sim_dict, net_dict, stim_dict2)
    time_network_B = time.time()
    # Create all nodes
    net_B.create()
    time_create_B = time.time()
    print("---> Connecting B network...")
    # Connect all nodes
    net_B.connect()
    time_connect_B = time.time()

    # Create network C
    print("---> Creating C network...")
    net_C = network.Network(sim_dict, net_dict)
    time_network_B = time.time()
    # Create all nodes
    net_C.create()
    time_create_C = time.time()
    print("---> Connecting C network...")
    # Connect all nodes
    net_C.connect()
    time_connect_C = time.time()

    #conn = nest.GetConnections().get()
    
    print("---> Connecting NETWORKS...")
    net_A.connect_networks(net_B, lateral_dict)
    #net_B.connect_networks(net_A, lateral_dict)
    net_A.connect_networks(net_C, lateral_dict)
    #net_C.connect_networks(net_A, lateral_dict)
    net_B.connect_networks(net_C, lateral_dict)
    #net_C.connect_networks(net_B, lateral_dict)

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
    raster_plot_interval = np.array([stim_dict['th_start'] - 100.0,
                                    stim_dict['th_start'] + 100.0 + sim_dict["t_sim"]])
    firing_rates_interval = np.array([sim_dict['t_presim'],
                                    sim_dict['t_presim'] + sim_dict['t_sim']])
    def map_pop(pops, network_name):
        return list(map(lambda pop: f"{pop}_{network_name}", pops))

    all_pops = map_pop(net_dict['populations'], "A") + map_pop(net_dict['populations'], "B") + map_pop(net_dict['populations'], "C")

    print('Interval to plot spikes: {} ms'.format(raster_plot_interval))
    if sim_dict.get("plot_raster", False):
        id_sim = sim_dict["data_path"].split("/")[-1]
        helpers.plot_raster(
            sim_dict["data_path"],
            'spike_recorder',
            raster_plot_interval[0],
            raster_plot_interval[1],
            net_dict['N_scaling'],
            all_pops,
            id_sim
        )
    print('Interval to compute firing rates: {} ms'.format(
        firing_rates_interval))
    if sim_dict.get("plot_firing_rates", False):
        helpers.firing_rates(
            sim_dict["data_path"], 
            'spike_recorder',
            firing_rates_interval[0], 
            firing_rates_interval[1])
        helpers.boxplot(sim_dict["data_path"], all_pops)
    if sim_dict.get("plot_voltages", False):
        helpers.plot_voltages(
            sim_dict["data_path"], 
            'voltmeter', 
            firing_rates_interval[0], 
            firing_rates_interval[1], 
            all_pops,
            'spike_recorder' if 'spike_recorder' in sim_dict["rec_dev"] else None,
            #self.input_meters.keys()
            net_A.input_meters.keys()
        )
    if sim_dict.get("plot_network", False):
        helpers.plot_network(
            sim_dict["data_path"],
            all_pops, 
            net_dict["conn_weights"],
            stim_dict["conn_weights_th"] if stim_dict["thalamic_input"] else None,
        )
    #net_A.evaluate(raster_plot_interval, firing_rates_interval)
    time_evaluate = time.time()

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
    plt.show()
