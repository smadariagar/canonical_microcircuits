import numpy as np

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

feedback_dict = {
    # factor to scale the number of neurons
    'N_scaling': 0.1,
    # factor to scale the indegrees
    'K_scaling': 0.1,
    # names of the simulated neuronal populations
    'populations': ['L23E', 'L23I', 'L4E', 'L4I', 'L5E', 'L5I', 'L6E', 'L6I'],
    # connection probabilities (the first index corresponds to the targets
    # and the second to the sources)

    # L4 source is local
    # Inhibitory connections are local (0 values)
    # L23E lateral
    # L5E lateral
    # L6E lateral
    'conn_probs': # segun wagatsuma 2013
        np.array(
            [[0.0, 0.0, 0.0, 0.0, 0.05,  0.0, 0.05,  0.0],      # L23E
             [0.0, 0.0, 0.0, 0.0, 0.02,  0.0, 0.02,  0.0],      # L23I
             [0.0, 0.0, 0.0, 0.0, 0.0,  0.0, 0.0,  0.0],      # L4E
             [0.0, 0.0, 0.0, 0.0, 0.0,  0.0, 0.0,  0.0],      # L4I
             [0.0, 0.0, 0.0, 0.0, 0.05,  0.0, 0.05,  0.0],      # L5E
             [0.0, 0.0, 0.0, 0.0, 0.02,  0.0, 0.02,  0.0],      # L5I
             [0.0, 0.0, 0.0, 0.0, 0.05,  0.0, 0.05,  0.0],      # L6E
             [0.0, 0.0, 0.0, 0.0, 0.02,  0.0, 0.02,  0.0]]),    # L6I
            # L23E L23I L4E  L4I  L5E   L5I  L6E   L6I

    # 'conn_probs': # segun wagatsuma 2013
    #     np.array(
    #         [[0.0, 0.0, 0.0, 0.0, 0.010, 0.0, 0.010, 0.0],      # L23E
    #          [0.0, 0.0, 0.0, 0.0, 0.035, 0.0, 0.035, 0.0],      # L23I
    #          [0.0, 0.0, 0.0, 0.0, 0.0,   0.0, 0.0, 0.0],      # L4E
    #          [0.0, 0.0, 0.0, 0.0, 0.0,   0.0, 0.0, 0.0],      # L4I
    #          [0.0, 0.0, 0.0, 0.0, 0.035, 0.0, 0.035, 0.0],      # L5E
    #          [0.0, 0.0, 0.0, 0.0, 0.035, 0.0, 0.035, 0.0],      # L5I
    #          [0.0, 0.0, 0.0, 0.0, 0.0,   0.0, 0.0, 0.0],      # L6E
    #          [0.0, 0.0, 0.0, 0.0, 0.0,   0.0, 0.0, 0.0]]),    # L6I
    #         # L23E L23I L4E  L4I   L5E    L5I   L6E   L6I

    # mean delay of excitatory connections (in ms)
    'delay_exc_mean': 8.0,
    # mean delay of inhibitory connections (in ms)
    'delay_inh_mean': 8.0,
    # relative standard deviation of the delay of excitatory and
    # inhibitory connections
    'delay_rel_std': 0.5,
}

updated_dict = {
    # matrix of mean delays
    'delay_matrix_mean': get_exc_inh_matrix(
        feedback_dict['delay_exc_mean'],
        feedback_dict['delay_inh_mean'],
        len(feedback_dict['populations']))}

feedback_dict.update(updated_dict)

