# -*- coding: utf-8 -*-
"""
Created on Wed May 10 11:52:40 2023

@author: blanchoy
"""
import bisect
import copy
import heapq
import itertools
import math
import matplotlib.pyplot as plt
plt.plot(), plt.close()
import numpy as np
import os
from functools import reduce
import time
import tracemalloc
import warnings

import Flexibility_1_2



p_demand = 1

tasks = ["Distribution"]
approaches = ["Structural"]   #   Operational   or Structural

Demand_file_name = None #"demand_file_adjusted_v3.txt"    # None or "file name"

piloted_productions_unit_names = ["EEU-1", "EEU-2", "EEU-3"]
piloted_productions_power_ranges = [[0, 30600], [0, 26000], [0, 6000]]
piloted_productions_power_steps = [180, 260, 300]  # Relative power steps

prod_absolute_steps = [int((max(i) - min(i)) * j) for i, j in zip(piloted_productions_power_ranges, piloted_productions_power_steps)]

gcd_step = int(reduce(math.gcd, prod_absolute_steps))

Flexibility_1_2.debug_print(prod_absolute_steps, "prod_absolute_steps")
Flexibility_1_2.debug_print(gcd_step, "gcd_step")
Flexibility_1_2.debug_print(type(gcd_step), "type of gcd step")

dissipation_unit_names = ["D-01"]
dissipation_power_ranges = [[-200]]
dissipation_power_steps = [200]

storage_units_names = ["S-01"]
storage_units_power_ranges = [[-200, 200]]  # [[P_max_ch1, P_max_disch1], ..., [P_max_chN, P_max_dischN]]
storage_units_power_steps = [[200]]

storage_discharge_unit_names = ["Discharge-1"]
storage_discharge_max_powers = [200]  # Same data as above, but for storage discharge

storage_discharge_min_powers = [200]
storage_discharge_power_steps = [200/(max(1, mx-mn)) for mx, mn in zip(storage_discharge_max_powers, storage_discharge_min_powers)]

storage_charge_unit_names = ["Charge-1"]
storage_charge_max_powers = [-200]  # Same as above, but for storage charge
storage_charge_min_powers = [-200]
storage_charge_power_steps = [200/(max(1, mx-mn)) for mx, mn in zip(storage_charge_max_powers, storage_charge_min_powers)]

dsm_range = [-200, 200]  # Maximum number of demand steps that can be displaced by means of DSM

imposed_productions_names = []
imposed_productions_max_powers = [0]  # Production that cannot be adjusted (e.g. renewables)
forbidden_combinations = [["Discharge-1", "Charge-1"]]







if __name__ == '__main__':

    power_ranges_prod_diss = piloted_productions_power_ranges + dissipation_power_ranges
    power_ranges_all_units_list = power_ranges_prod_diss + storage_units_power_ranges
    # fixme
    if True:
       Flexibility_1_2.assess_flexibility(task = tasks, 
                                          approach = approaches, 
                                          demand = p_demand,
                                          p_step_productions = piloted_productions_power_steps, 
                                          p_max_discharges = storage_discharge_max_powers, 
                                          p_min_discharges = storage_discharge_min_powers,
                                          p_step_discharges = storage_discharge_power_steps, 
                                          p_max_charges = storage_charge_max_powers, 
                                          p_min_charges = storage_charge_min_powers,
                                          p_step_charges = storage_charge_power_steps, 
                                          p_step_dissipation = dissipation_power_steps,
                                          p_max_imposed = imposed_productions_max_powers, 
                                          forbid_combi_user = forbidden_combinations,
                                          prod_names = piloted_productions_unit_names, 
                                          discharge_names = storage_discharge_unit_names,
                                          charge_names = storage_charge_unit_names, 
                                          dissip_names = dissipation_unit_names, 
                                          flexi_dsm = dsm_range,
                                          p_ranges_prods = piloted_productions_power_ranges,
                                          p_ranges_diss = dissipation_power_ranges,  
                                          p_ranges_storages = storage_units_power_ranges,
                                          multipurpose_step = gcd_step,
                                          Demand_file_name = Demand_file_name)