net_dict = {
    # neuron model
    'neuron_model': 'iaf_psc_alpha',
    # names of the simulated neuronal populations
    'populations': ['smooth_cells', "P23", "P56"],
    # number of neurons in the different populations (same order as
    # 'populations')
    'full_num_neurons':
        np.array([20683, 5834, 21915]),
    'neuron_params': {
        'smooth_cells': {
            # reset membrane potential of the neurons (in mV)
            'E_L': -65.0,
            # threshold potential of the neurons (in mV)
            'V_th': -50.0,
            # membrane potential after a spike (in mV)
            'V_reset': -65.0,
        },
        'P23': {
            # reset membrane potential of the neurons (in mV)
            'E_L': -65.0,
            # threshold potential of the neurons (in mV)
            'V_th': -50.0,
            # membrane potential after a spike (in mV)
            'V_reset': -65.0,
        },
        'P56': {
            # reset membrane potential of the neurons (in mV)
            'E_L': -65.0,
            # threshold potential of the neurons (in mV)
            'V_th': -50.0,
            # membrane potential after a spike (in mV)
            'V_reset': -65.0,
        }
    },
    # connection weights (the first index corresponds to the targets
    # and the second to the sources)
    "conn_weights": np.array([
            [-10, 10, 10],
            [-10, 10, 10],
            [-20, 10, 10]
        ])

    # "connections": {
    #     "smooth_cells": {
    #         "smooth_cells": -10, # inhibitory connection
    #         "P23": -10, # inhibitory connection
    #         "P56": -20, # stronger inhibitory connection
    #     },
    #     "P23": {
    #         "smooth_cells": 10, # excitatory connection
    #         "P23": 10, # excitatory connection
    #         "P56": 10, # excitatory connection
    #     },
    #     "P56": {
    #         "smooth_cells": 10, # excitatory connection
    #         "P23": 10, # excitatory connection
    #         "P56": 10, # excitatory connection
    #     },
    #     "thalamus": {
    #         "smooth_cells": 10, # excitatory connection
    #         "P23": 10, # excitatory connection
    #         "P56": 5, # weak connection
    #     }
    # }   
}
    