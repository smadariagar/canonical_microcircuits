import os 

import nest
import time
import numpy as np
import matplotlib.pyplot as plt

from assets.potjans_diesmann.stimulus_params import stim_dict
from assets.potjans_diesmann.stimulus_params2 import stim_dict as stim_dict2
from assets.potjans_diesmann.network_params import net_dict
from assets.potjans_diesmann.sim_params import sim_dict
from assets.potjans_diesmann.lateral_params import lateral_dict
from . import network_potjans_diesmann as network

from utils import helpers

if __name__ == '__main__':

    id_sim = "20231017152519"   

    data_path = os.path.join(os.getcwd(), 'results/potjans_diesmann/', id_sim)

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

    all_pops = list(map(lambda pop: f"{pop}_src", net_dict['populations'])) + list(map(lambda pop: f"{pop}_tg", net_dict['populations']))
    print('Interval to plot spikes: {} ms'.format(raster_plot_interval))
    if sim_dict.get("plot_raster", False):
        helpers.plot_raster(
            data_path,
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
            data_path, 
            'spike_recorder',
            firing_rates_interval[0], 
            firing_rates_interval[1])
        helpers.boxplot(data_path, all_pops)
    if sim_dict.get("plot_voltages", False):
        helpers.plot_voltages(
            data_path, 
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
            data_path,
            all_pops, 
            net_dict["conn_weights"],
            stim_dict["conn_weights_th"] if stim_dict["thalamic_input"] else None,
        )
    #net_src.evaluate(raster_plot_interval, firing_rates_interval)
    time_evaluate = time.time()

    plt.show()
