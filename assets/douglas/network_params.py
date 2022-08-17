import numpy as np

net_dict = {
    # factor to scale the number of neurons
    'N_scaling': 1,
    # neuron model
    'neuron_model': 'iaf_psc_alpha',
    # names of the simulated neuronal populations
    'populations': ['smooth_cells', "P23", "P56"],
    # number of neurons in the different populations (same order as
    # 'populations')
    'full_num_neurons':
        np.array([1, 1, 1]),
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
        ]),
    # turn Poisson input on or off (True or False)
    # if False: DC input is applied for compensation
    'poisson_input': False,
    # indegree of external connections to the different populations (same order
    # as in 'populations')
    'K_ext': np.array([1, 1, 1])*1000,
    # rate of the Poisson generator (in spikes/s)
    'bg_rate': 8.,
    # delay from the Poisson generator to the network (in ms)
    'delay_poisson': 1.5,
}
    