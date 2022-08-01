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
        },
        'P23': {
        },
        'P56': {
        }
    },
}
    