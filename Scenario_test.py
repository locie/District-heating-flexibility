# -*- coding: utf-8 -*-
"""
Created on Wed May 10 11:36:51 2023

@author: blanchoy
"""


from Flexibility_1_2 import *


p_demand = 1

# TODO: Raise ValueError if the user provides p_max < p_min.
# TODO: The tool does not consider the possibility of not selecting any unit at all. Solve that.
# TODO: p_max_dissipation = 0 or = -1 should give same results, but they don't. Redundant solutions somewhere. Solve it.

# ---------------------
# ILLUSTRATIVE SCENARIO
# ---------------------

tasks = ["Distribution"]
approaches = ["Structural"]    # "Structural", "Operational" or "Both"

demand_file_name = "demand_file_adjusted_v3.txt"    # None or "file name"

piloted_productions_unit_names = ["P1_1", "P1_2" , "P1_3" , "P2_1", "P2_1" ,"P3_1" ]  # List your units' names
piloted_productions_power_ranges = [[900*0.2, 900],  [900*0.2, 900] , [900*0.2, 900] , [1300*0.2, 1300] , [1300*0.2, 1300] , [1450*0.2, 1450]] #  =============================== plus de step mais liste des puissance ========================  max-min for each unit  
piloted_productions_power_steps = [900*0.8, 900*0.8 , 900*0.8 ,1300*0.8 , 1300*0.8, 1450*0.8]  # Relative power steps

dissipation_unit_names = ["D-01"]
dissipation_power_ranges = [[-10]]  # Do not include the zero, it is done automatically
dissipation_power_steps = [10]  # Relative power steps

storage_units_names = ["S-01"]
storage_units_power_ranges = [[-10, 10]]  # [[P_max_charge1, P_max_discharge1], ..., [P_max_chargeN, P_max_dischargeN]]
storage_units_power_steps = [10, 10]

dsm_range = [-10, 10]  # Range of maximal diversion through Demand Side Management (DSM) conveyed as: [-x, x]

imposed_productions_names = ["IP-1"]
imposed_productions_max_powers = []  # Production that cannot be adjusted (e.g. renewables)

gcd_step = 10
forbidden_combinations = [["Discharge-1", "Charge-1"]]


if __name__ == '__main__':

    power_ranges_prod_diss = piloted_productions_power_ranges + dissipation_power_ranges
    power_ranges_all_units_list = power_ranges_prod_diss + storage_units_power_ranges
    # fixme
    if True:
       assess_flexibility(task = tasks, 
                                          approach = approaches, 
                                          demand = p_demand,
                                          p_step_productions = piloted_productions_power_steps,
                                          p_step_dissipation = dissipation_power_steps,
                                          p_max_imposed = imposed_productions_max_powers, 
                                          forbid_combi_user = forbidden_combinations,
                                          prod_names = piloted_productions_unit_names,
                                          dissip_names = dissipation_unit_names, 
                                          flexi_dsm = dsm_range,
                                          p_ranges_prods = piloted_productions_power_ranges,
                                          p_ranges_diss = dissipation_power_ranges,  
                                          p_ranges_storages = storage_units_power_ranges,
                                          p_step_storages = storage_units_power_steps,
                                          multipurpose_step = gcd_step,
                                          demand_file_name = demand_file_name)