# -*- coding: utf-8 -*-
#
# network_params.py
#
# This file is part of NEST.
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

"""PyNEST Microcircuit: Network Parameters
---------------------------------------------

A dictionary with base network and neuron parameters is enhanced with derived
parameters.

"""

import numpy as np
import copy

def get_exc_inh_matrix(val_exc, val_inh, num_pops):
    """ Creates a matrix for excitatory and inhibitory values.

    Parameters
    ----------
    val_exc
        Excitatory value.
    val_inh
        Inhibitory value.
    num_pops
        Number of populations.

    Returns
    -------
    matrix
        A matrix of of size (num_pops x num_pops).

    """
    matrix = np.zeros((num_pops, num_pops))
    matrix[:, 0:num_pops:2] = val_exc
    matrix[:, 1:num_pops:2] = val_inh
    return matrix

def update_derived_matrices(d):
    """
    Calcula y añade las matrices derivadas (PSP y delays) a un diccionario de red.
    """
    # 1. Deriva la matriz de PSPs medios
    PSP_matrix_mean = get_exc_inh_matrix(
        d['PSP_exc_mean'],
        d['PSP_exc_mean'] * d['g'],
        len(d['populations'])
    )
    
    # 2. Duplica el PSP medio para la conexión de L4E a L23E
    PSP_matrix_mean[0, 2] = 2. * d['PSP_exc_mean']

    # 3. Deriva la matriz de delays y actualiza el diccionario directamente
    d['PSP_matrix_mean'] = PSP_matrix_mean
    d['delay_matrix_mean'] = get_exc_inh_matrix(
        d['delay_exc_mean'],
        d['delay_inh_mean'],
        len(d['populations'])
    )

net_dict = {
    # factor to scale the number of neurons
    'N_scaling': 1.0,
    # factor to scale the indegrees
    'K_scaling': 1.0,
    # neuron model
    'neuron_model': 'iaf_psc_exp',
    # names of the simulated neuronal populations
    'populations': ['E', 'I'],
    # number of neurons in the different populations (same order as
    # 'populations')
    'full_num_neurons': np.array([400, 100]),
    # mean rates of the different populations in the non-scaled version of the
    # microcircuit (in spikes/s; same order as in 'populations');
    # necessary for the scaling of the network.
    # The values were obtained by running this PyNEST microcircuit without MPI,
    # 'local_num_threads' 4 and both 'N_scaling' and 'K_scaling' set to 1.
    "full_mean_rates": np.array([1, 3]),
    # connection probabilities (the first index corresponds to the targets
    # and the second to the sources)
    'conn_probs': np.array(
        [
            [0.1009, 0.1689], # E
            [0.1346, 0.1371], # I
            # E       I    
        ]
    ),
    # mean amplitude of excitatory postsynaptic potential (in mV)
    'PSP_exc_mean': 0.15,
    # relative standard deviation of the weight
    'weight_rel_std': 0.1,
    # relative inhibitory weight
    'g': -4,
    # mean delay of excitatory connections (in ms)
    'delay_exc_mean': 1.5,
    # mean delay of inhibitory connections (in ms)
    'delay_inh_mean': 0.75,
    # relative standard deviation of the delay of excitatory and
    # inhibitory connections
    'delay_rel_std': 0.5,

    # turn Poisson input on or off (True or False)
    # if False: DC input is applied for compensation
    'poisson_input': True,
    'dc_compensation': False,
    # indegree of external connections to the different populations (same order
    # as in 'populations')
    'K_ext': np.array([1600, 1500]),
    # rate of the Poisson generator (in spikes/s)
    'bg_rate': 8.,
    # delay from the Poisson generator to the network (in ms)
    'delay_poisson': 1.5,

    # initial conditions for the membrane potential, options are:
    # 'original': uniform mean and standard deviation for all populations as
    #             used in earlier implementations of the model
    # 'optimized': population-specific mean and standard deviation, allowing a
    #              reduction of the initial activity burst in the network
    #              (default)
    'V0_type': 'optimized',
    # parameters of the neuron model
    'neuron_params': {
        # membrane potential average for the neurons (in mV)
        'V0_mean': {'original': -58.0,
                    'optimized': [-68.28, -63.16, -63.33, -63.45,
                                  -63.11, -61.66, -66.72, -61.43]},
        # standard deviation of the average membrane potential (in mV)
        'V0_std': {'original': 10.0,
                   'optimized': [5.36, 4.57, 4.74, 4.94,
                                 4.94, 4.55, 5.46, 4.48]},
        # reset membrane potential of the neurons (in mV)
        'E_L': -65.0,
        # threshold potential of the neurons (in mV)
        'V_th': -50.0,
        # membrane potential after a spike (in mV)
        'V_reset': -65.0,
        # membrane capacitance (in pF)
        'C_m': 250.0,
        # membrane time constant (in ms)
        'tau_m': 10.0,
        # time constant of postsynaptic currents (in ms)
        'tau_syn': 0.5,
        # refractory period of the neurons after a spike (in ms)
        't_ref': 2.0}
    }

update_derived_matrices(net_dict)
