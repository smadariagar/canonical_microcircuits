import nest
import time
import numpy as np
import matplotlib.pyplot as plt

from assets.potjans_diesmann.stimulus_params import stim_dict
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
    # Create network
    print("---> Creating SOURCE network...")
    net_src = network.Network(sim_dict, net_dict, stim_dict)
    time_network_src = time.time()
    # Create all nodes
    net_src.create()
    time_create_src = time.time()
    # Connect all nodes
    print("---> Connecting source network...")
    net_src.connect()
    time_connect_src = time.time()
    # Create network
    print("---> Creating TARGET network...")
    net_tg = network.Network(sim_dict, net_dict, stim_dict)
    time_network_tg = time.time()
    # Create all nodes
    net_tg.create()
    time_create_tg = time.time()
    print("---> Connecting target network...")
    # Connect all nodes
    net_tg.connect()
    time_connect_tg = time.time()

    #conn = nest.GetConnections().get()
    
    print("---> Connecting NETWORKS...")
    net_src.connect_networks(net_tg, lateral_dict)

    nest.Prepare()
    nest.Cleanup()

    print('---> Simulating...')
    net_src.simulate(sim_dict['t_sim'])
    time_simulate = time.time()

    ###############################################################################
    # Plot a spike raster of the simulated neurons and a box plot of the firing
    # rates for each population.
    # For visual purposes only, spikes 100 ms before and 100 ms after the thalamic
    # stimulus time are plotted here by default.
    # The computation of spike rates discards the presimulation time to exclude
    # initialization artifacts.
    print('---> Evaluating...')
    raster_plot_interval = np.array([stim_dict['th_start'] - 300.0,
                                    stim_dict['th_start'] + 300.0])
    firing_rates_interval = np.array([sim_dict['t_presim'],
                                    sim_dict['t_presim'] + sim_dict['t_sim']])

    all_pops = list(map(lambda pop: f"{pop}_src", net_dict['populations'])) + list(map(lambda pop: f"{pop}_tg", net_dict['populations']))
    print('Interval to plot spikes: {} ms'.format(raster_plot_interval))
    if sim_dict.get("plot_raster", False):
        helpers.plot_raster(
            sim_dict["data_path"],
            'spike_recorder',
            raster_plot_interval[0],
            raster_plot_interval[1],
            net_dict['N_scaling'],
            all_pops,
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
            net_src.input_meters.keys()
        )
    if sim_dict.get("plot_network", False):
        helpers.plot_network(
            sim_dict["data_path"],
            all_pops, 
            net_dict["conn_weights"],
            stim_dict["conn_weights_th"] if stim_dict["thalamic_input"] else None,
        )
    #net_src.evaluate(raster_plot_interval, firing_rates_interval)
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
            time_network_src -
            time_start) +
        '  Time to create:      {:.3f} s\n'.format(
            time_create_src -
            time_network_src) +
        '  Time to connect:     {:.3f} s\n'.format(
            time_connect_src -
            time_create_src) +
        '  Time to presimulate: {:.3f} s\n'.format(
            time_simulate -
            time_connect_src) +
        '  Time to simulate:    {:.3f} s\n'.format(
            time_simulate -
            time_connect_src) +
        '  Time to evaluate:    {:.3f} s\n'.format(
            time_evaluate -
            time_simulate))
    plt.show()
