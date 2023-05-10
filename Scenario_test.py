# -*- coding: utf-8 -*-
"""
Created on Wed May 10 11:36:51 2023

@author: blanchoy
"""

import Flexibility_1_2


p_demand = 1

# TODO: Raise ValueError if the user provides p_max < p_min.
# TODO: The tool does not consider the possibility of not selecting any unit at all. Solve that.
# TODO: p_max_dissipation = 0 or = -1 should give same results, but they don't. Redundant solutions somewhere. Solve it.

# ---------------------
# ILLUSTRATIVE SCENARIO
# ---------------------

tasks = ["Distribution", "Distribution"]
approaches = ["Structural", "Operational"]    # "Structural", "Operational" or "Both"
# tasks = ["Distribution"]
# approaches = ["Both"]

Demand_file_name = None #"demand_file_adjusted_v3.txt"    # None or "file name"

piloted_productions_unit_names = ["P-01", "P-02", "P-03"]  # List your units' names
piloted_productions_power_ranges = [[2, 3], [3, 4], [14, 15]]  #max-min for each unit
piloted_productions_power_steps = [1, 1, 1]  # Relative power steps

gcd_step = 1

dissipation_unit_names = ["D-01"]
dissipation_power_ranges = [[-1]]  # Do not include the zero, it is done automatically
dissipation_power_steps = [1]  # Relative power steps

storage_units_names = ["S-01"]
storage_units_power_ranges = [[-1, 1]]  # [[P_max_charge1, P_max_discharge1], ..., [P_max_chargeN, P_max_dischargeN]]
storage_units_power_steps = [[1]]

storage_discharge_unit_names = ["Discharge-1"]
storage_discharge_max_powers = [1]  # Same data as above, but for storage discharge
storage_discharge_min_powers = [1]
storage_discharge_power_steps = [1/(max(1, mx-mn)) for mx, mn in zip(storage_discharge_max_powers, storage_discharge_min_powers)]

storage_charge_unit_names = ["Charge-1"]
storage_charge_max_powers = [-1]  # Same as above, but for storage charge
storage_charge_min_powers = [-1]
storage_charge_power_steps = [1/(max(1, mx-mn)) for mx, mn in zip(storage_charge_max_powers, storage_charge_min_powers)]

dsm_range = [-1, 1]  # Range of maximal diversion through Demand Side Management (DSM) conveyed as: [-x, x]

imposed_productions_names = ["IP-1"]
imposed_productions_max_powers = []  # Production that cannot be adjusted (e.g. renewables)

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