# -*- coding: utf-8 -*-
#
# run_model.py
#
# Este código debería correr todas las variables de mi modelo.
# Todo el modelo está construido sobre NEST
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

"""Run Simulation
-----------------------------------------

Este script corre el modelo de corteza visual, con módulos de microcircuito tanto en V1 como en V2.

"""

###############################################################################
# Import the necessary modules and start the time measurements.
import time
import os
from random import randint
import json
import nest
import numpy as np

from utils import helpers

from assets.potjans_diesmann.sim_params import sim_dict # simulación

from assets.potjans_diesmann.stimulus_params1 import stim_dict1
from assets.potjans_diesmann.stimulus_params2 import stim_dict2
from assets.potjans_diesmann.stimulus_params3 import stim_dict3

from assets.potjans_diesmann.lateral_params import lateral_dict

from assets.potjans_diesmann.network_params import net_dict #para cada microcircuito es igual

from . import network_potjans_diesmann as network

if __name__ == '__main__':

    time_start = time.time()

    