import numpy as np

lateral_dict = {
    # factor to scale the number of neurons
    'N_scaling': 0.2,
    # factor to scale the indegrees
    'K_scaling': 0.1,
    # names of the simulated neuronal populations
    #'populations': ['L23E', 'L23I', 'L4E', 'L4I', 'L5E', 'L5I', 'L6E', 'L6I'],
    # connection probabilities (the first index corresponds to the targets
    # and the second to the sources)

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
             # L23E  L23I L4E  L4I   L5E   L5I   L6E   L6I
}