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



lateral_dict_near = {
    # factor to scale the number of neurons
    'N_scaling': 0.1,
    # factor to scale the indegrees
    'K_scaling': 0.3,
    # names of the simulated neuronal populations
    'populations': ['L23E', 'L23I', 'L4E', 'L4I', 'L5E', 'L5I', 'L6E', 'L6I'],
    # connection probabilities (the first index corresponds to the targets and the second to the sources)
    # L4 source is local
    # Inhibitory connections are local (0 values)
    # L23E lateral
    # L5E lateral
    # L6E lateral
    'conn_probs': # segun wagatsuma 2013
        np.array(
            [[0.06, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],      # L23E
             [0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],      # L23I
             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],      # L4E
             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],      # L4I
             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],      # L5E
             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],      # L5I
             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],      # L6E
             [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]]),    # L6I
            # L2E  L2I  L4E  L4I  L5E  L5I  L6E  L6I
    # Parámetros de la sinapsis            
    'synapse_params': {
        'synapse_model': 'stdp_synapse',
        'weight': 1.0,      # Peso inicial
        'delay': 5.0,       # Delay (puedes usar tu delay_exc_mean aquí)
        'alpha': 1.0,       # Factor de asimetría
        'lambda': 0.01,     # Tasa de aprendizaje
        'tau_plus': 20.0,   # Constante de tiempo potenciar (ms)
        'Wmax': 100.0       # Peso máximo permitido
    },
    # mean delay of excitatory connections (in ms)
    'delay_exc_mean': 5.0,
    # mean delay of inhibitory connections (in ms)
    'delay_inh_mean': 3.0,
    # relative standard deviation of the delay of excitatory and
    # inhibitory connections
    'delay_rel_std': 1.5
}

lateral_dict_far = copy.deepcopy(lateral_dict_near)

lateral_dict_far['conn_probs'] = np.array([
    [0.005, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],   # L23E
    [0.03, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],   # L23I
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],   # L4E
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],   # L4I
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],   # L5E
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],   # L5I
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],   # L6E
    [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],   # L6I
])

lateral_dict_far['delay_exc_mean'] = 8.0
lateral_dict_far['delay_inh_mean'] = 5.0
lateral_dict_far['delay_rel_std'] = 2.5
    

def update_lateral_delays(lat_dict):
    """
    Calcula y añade la matriz de delays a un diccionario de conexiones laterales.
    """
    lat_dict['delay_matrix_mean'] = get_exc_inh_matrix(
        lat_dict['delay_exc_mean'],
        lat_dict['delay_inh_mean'],
        len(lat_dict['populations'])
    )

update_lateral_delays(lateral_dict_near)
update_lateral_delays(lateral_dict_far)