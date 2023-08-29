import numpy as np

lateral_dict = {
    # factor to scale the number of neurons
    'N_scaling': 0.1,
    # factor to scale the indegrees
    'K_scaling': 0.1,
    # names of the simulated neuronal populations
    'populations': ['L23E', 'L23I', 'L4E', 'L4I', 'L5E', 'L5I', 'L6E', 'L6I'],
    # connection probabilities (the first index corresponds to the targets
    # and the second to the sources)
    'conn_probs':
        np.array(
            [[0.1009, 0.1689, 0.0437, 0.0818, 0.0323, 0., 0.0076, 0.],
             [0.1346, 0.1371, 0.0316, 0.0515, 0.0755, 0., 0.0042, 0.],
             [0.0077, 0.0059, 0.0497, 0.135, 0.0067, 0.0003, 0.0453, 0.],
             [0.0691, 0.0029, 0.0794, 0.1597, 0.0033, 0., 0.1057, 0.],
             [0.1004, 0.0622, 0.0505, 0.0057, 0.0831, 0.3726, 0.0204, 0.],
             [0.0548, 0.0269, 0.0257, 0.0022, 0.06, 0.3158, 0.0086, 0.],
             [0.0156, 0.0066, 0.0211, 0.0166, 0.0572, 0.0197, 0.0396, 0.2252],
             [0.0364, 0.001, 0.0034, 0.0005, 0.0277, 0.008, 0.0658, 0.1443]]),
    # mean amplitude of excitatory postsynaptic potential (in mV)
    'PSP_exc_mean': 0.15,
    # relative inhibitory weight
    'g': -4,
}
# derive matrix of mean PSPs,
# the mean PSP of the connection from L4E to L23E is doubled
PSP_matrix_mean = get_exc_inh_matrix(
    lateral_dict['PSP_exc_mean'],
    lateral_dict['PSP_exc_mean'] * lateral_dict['g'],
    len(lateral_dict['populations'])
)
PSP_matrix_mean[0, 2] = 2. * lateral_dict['PSP_exc_mean']

updated_dict = {
    # matrix of mean PSPs
    'PSP_matrix_mean': PSP_matrix_mean,
}

net_dict.update(updated_dict)