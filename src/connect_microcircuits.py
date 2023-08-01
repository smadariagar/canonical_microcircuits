import nest

import numpy as np
import matplotlib.pyplot as plt

from assets.potjans_diesmann.stimulus_params import stim_dict
from assets.potjans_diesmann.network_params import net_dict
from assets.potjans_diesmann.sim_params import sim_dict
from . import network_potjans_diesmann as network

if __name__ == '__main__':

    net_src = network.Network(sim_dict, net_dict, stim_dict)
    net_src.create()
    net_src.connect()

    net_tg = network.Network(sim_dict, net_dict, stim_dict)
    net_tg.create()
    net_tg.connect()

    #conn = nest.GetConnections().get()

    #print(conn.get())

    net_src.connect_networks(net_tg, 'all_to_all')

    #nest.Connect(net_1, net_2, 'all_to_all')
    #print(net_1.pops)