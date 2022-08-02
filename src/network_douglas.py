import os
import numpy as np
import nest
from utils import helpers
import warnings

from network import Network

class NetworkDouglas(Network):
    """ Provides functions to setup NEST, to create and connect all nodes of
    the network, to simulate, and to evaluate the resulting spike data.

    Instantiating a Network object derives dependent parameters and already
    initializes the NEST kernel.

    Implementation:
    ------------
    RODNEY J. DOUGLAS*t AND KEVAN A. C. MARTIN* 
    A FUNCTIONAL MICROCIRCUIT FOR CAT VISUAL CORTEX

    Parameters
    ---------
    sim_dict
        Dictionary containing all parameters specific to the simulation
        (see: ``sim_params.py``).
    net_dict
         Dictionary containing all parameters specific to the neuron and
         network models (see: ``network_params.py``).
    stim_dict
        Optional dictionary containing all parameter specific to the stimulus
        (see: ``stimulus_params.py``)

    """
    def __init__(self, sim_dict, net_dict, stim_dict=None):
        super().__init__(sim_dict, net_dict, stim_dict)

    def __derive_parameters(self):
        """
        Derives and adjusts parameters and stores them as class attributes.
        """
        self.population_names = self.net_dict["populations"]
        self.num_pops = len(self.population_names)
        self.num_neurons = self.net_dict["full_num_neurons"]
        self.conn_weights = self.net_dict["conn_weights"]

    def __setup_nest(self):
        """ Initializes the NEST kernel.

        Reset the NEST kernel and pass parameters to it.
        """
        super().__setup_nest()

    def create(self):
        """ Creates all network nodes.

        Neuronal populations and recording and stimulation devices are created.

        """
        super().create()

    def connect(self):
        """ Connects all network nodes.

        Connects all neuronal populations and recording and stimulation
        devices.

        """
        super().connect()

    def simulate(self):
        """ Simulates the network.

        Simulates the network for the specified duration.

        """
        super().simulate()

    def __create_neuronal_populations(self):
        """ Creates the neuronal populations.

        Creates the neuronal populations and stores them as class attributes.

        """
        self.pops = []
        for i in range(self.num_pops):
            # Get associated neuron params from the specific population
            neuron_params = self.net_dict["neuron_params"][self.population_names[i]]
            # Create the population
            population = nest.Create(self.net_dict["neuron_model"],
                                    self.num_neurons[i])
            population.set(**neuron_params)
            # Store the population
            self.pops.append(population)

    def __create_recording_devices(self):
        """ Creates one recording device of each kind per population.

        Only devices which are given in ``sim_dict['rec_dev']`` are created.

        """
        if 'spike_recorder' in self.sim_dict['rec_dev']:
            sr_dict = {}
            self.spike_recorders = nest.Create('spike_recorder',
                                               n=self.num_pops,
                                               params=sr_dict)
    
        if 'voltmeter' in self.sim_dict['rec_dev']:
            vm_dict = {'record_from': ['V_m']}
            self.voltmeters = nest.Create('voltmeter',
                                          n=self.num_pops,
                                          params=vm_dict)

    def __connect_neuronal_populations(self):
        """ Creates the connections between neuronal populations. """
        for i, target_pop in enumerate(self.pops):
            for j, source_pop in enumerate(self.pops):
                conn_dict_rec = {
                }
                syn_dict = {
                    'synapse_model': 'static_synapse',
                    'weight': self.conn_weights[i][j],
                }

                nest.Connect(
                    source_pop, target_pop,
                    conn_spec=conn_dict_rec,
                    syn_spec=syn_dict)
