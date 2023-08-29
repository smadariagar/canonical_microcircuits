import nest
import time
import numpy as np
import matplotlib.pyplot as plt

from assets.potjans_diesmann.stimulus_params import stim_dict
from assets.potjans_diesmann.network_params import net_dict
from assets.potjans_diesmann.sim_params import sim_dict
from assets.potjans_diesmann.lateral_params import lateral_dict
from . import network_potjans_diesmann as network

if __name__ == '__main__':

    nest.ResetKernel()

    net_src = network.Network(sim_dict, net_dict, stim_dict)
    net_src.create()
    net_src.connect()

    net_tg = network.Network(sim_dict, net_dict, stim_dict)
    net_tg.create()
    net_tg.connect()

    #conn = nest.GetConnections().get()

    #print(conn.get())

    net_src.connect_networks(net_tg, lateral_dict)

    #nest.Connect(net_1, net_2, 'all_to_all')
    #print(net_1.pops)

    net_src.simulate(sim_dict['t_sim'])
    time_simulate = time.time()

    ###############################################################################
    # Plot a spike raster of the simulated neurons and a box plot of the firing
    # rates for each population.
    # For visual purposes only, spikes 100 ms before and 100 ms after the thalamic
    # stimulus time are plotted here by default.
    # The computation of spike rates discards the presimulation time to exclude
    # initialization artifacts.

    raster_plot_interval = np.array([stim_dict['th_start'] - 100.0,
                                    stim_dict['th_start'] + 100.0])
    firing_rates_interval = np.array([sim_dict['t_presim'],
                                    sim_dict['t_presim'] + sim_dict['t_sim']])
    net_src.evaluate(raster_plot_interval, firing_rates_interval)
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
            time_network -
            time_start) +
        '  Time to create:      {:.3f} s\n'.format(
            time_create -
            time_network) +
        '  Time to connect:     {:.3f} s\n'.format(
            time_connect -
            time_create) +
        '  Time to presimulate: {:.3f} s\n'.format(
            time_presimulate -
            time_connect) +
        '  Time to simulate:    {:.3f} s\n'.format(
            time_simulate -
            time_presimulate) +
        '  Time to evaluate:    {:.3f} s\n'.format(
            time_evaluate -
            time_simulate))

    plt.show()
