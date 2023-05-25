# -*- coding: utf-8 -*-
"""
Created on Wed May 10 11:36:51 2023

@author: blanchoy
"""


from Flexibility_1_2 import *
import math


p_demand = 1

# TODO: Raise ValueError if the user provides p_max < p_min.
# TODO: The tool does not consider the possibility of not selecting any unit at all. Solve that.
# TODO: p_max_dissipation = 0 or = -1 should give same results, but they don't. Redundant solutions somewhere. Solve it.

# ---------------------
# ILLUSTRATIVE SCENARIO
# ---------------------

tasks = ["Distribution"]
approaches = ["Operational"]    # "Structural" or "Operational"

demand_file_name = "demand_file_adjusted_v3.txt"    # None or "file name"

""" Enter below the input data for your equivalent energy units. The list of powers must contain EVERY output power 
 that the unit can be adjusted to. For example, for a unit operating between 200 MW and 800 MW by steps of 200 MW,
 the list of powers is: [200, 400, 600, 800]. No need to include the 0 because Flextropy inserts it by default. """

piloted_productions_unit_names = ["P-01", "P-02"]  # Units names
piloted_productions_power_ranges = [[40, 80, 120, 160, 200], [40, 80, 120, 160, 200]]  # EVERY adjustable power

dissipation_unit_names = ["D-01"]  # Units names
dissipation_power_ranges = [[-120, -80, -40]]  # EVERY adjustable power

storage_units_names = ["S-01", "S-02"]  # Units names
storage_units_power_ranges = [[-80, 80], [-160, 240]]  # EVERY adjustable power

dsm_range = [0, 0]  # Range of maximal diversion through Demand Side Management (DSM) conveyed as: [-x, x]

imposed_productions_names = ["IP-1"]
imposed_productions_max_powers = []  # Production that cannot be adjusted (e.g. renewables)

gcd_step = 40  # User must make sure this gcd is coherent with the powers lists declared for all units

forbidden_combinations = [["Discharge-1", "Charge-1"]]

if __name__ == '__main__':

    power_ranges_prod_diss = piloted_productions_power_ranges + dissipation_power_ranges
    power_ranges_all_units_list = power_ranges_prod_diss + storage_units_power_ranges
    # fixme
    if True:
       assess_flexibility(task = tasks, 
                                          approach = approaches, 
                                          demand = p_demand,
                                          p_max_imposed = imposed_productions_max_powers, 
                                          forbid_combi_user = forbidden_combinations,
                                          prod_names = piloted_productions_unit_names,
                                          dissip_names = dissipation_unit_names, 
                                          flexi_dsm = dsm_range,
                                          p_ranges_prods = piloted_productions_power_ranges,
                                          p_ranges_diss = dissipation_power_ranges,  
                                          p_ranges_storages = storage_units_power_ranges,
                                          multipurpose_step = gcd_step,
                                          demand_file_name = demand_file_name)