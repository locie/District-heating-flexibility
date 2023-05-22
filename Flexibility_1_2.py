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
# fixme
# from collections import Counter


# general formulation of the problem:
# this physical problem may probably be solved using a MIP algorithm (Mixed-Integer). If so, it would be less time-consuming

# general fixme:
# consider the use of numpy arrays
# same names must be use for same instances
def assess_flexibility(task, 
                       approach, 
                       demand, 
                       p_ranges_prods: list = None, 
                       p_step_productions: list = None,
                       p_ranges_storages: list = None, 
                       p_max_discharges: list = None, 
                       p_min_discharges: list = None,
                       p_step_discharges: list = None, 
                       p_max_charges: list = None, 
                       p_min_charges: list = None,
                       p_step_charges: list = None, 
                       p_ranges_diss: list = None, 
                       p_step_dissipation: list = None,
                       p_max_imposed=None, 
                       flexi_dsm: list = None, 
                       forbid_combi_user: list = None,
                       prod_names: list = None, 
                       discharge_names: list = None, 
                       charge_names: list = None,
                       dissip_names: list = None, 
                       prod_ranges=None, 
                       multipurpose_step: int = None,
                       Demand_file_name = None):
    tracemalloc.start()  # Track memory allocation
    tic_overall = time.time()  # Initialize clock

    print("\n")

    print("  ")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("~~~ WELCOME TO THE FLEXIBILITY WIZARD ~~~")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")

    p_max_productions = [max(p) for p in p_ranges_prods]
    p_min_productions = [min(p) for p in p_ranges_prods]
    p_max_dissipation = [min(p) for p in p_ranges_diss]  # The most negative dissipation power
    p_min_dissipation = [max(p) for p in p_ranges_diss]  # The least negative dissipation power
    # TODO: Manage to model storage as one unit but with minimal charge and discharge powers?
    # p_max_discharges_2 = [max(p) for p in p_ranges_storages]
    # p_min_discharges_2 = [min(p) for p in p_ranges_storages]
    # debug_print(p_max_discharges, "p_max_discharges")
    # debug_print(p_max_discharges_2, "p_max_discharges_2")
    # debug_print(p_min_discharges, "p_min_discharges")
    # debug_print(p_min_discharges_2, "p_min_discharges_2")

    p_ranges_prod_diss = p_ranges_prods + p_ranges_diss
    p_ranges_all_units = p_ranges_prods + p_ranges_diss + p_ranges_storages

    # BUILD DEMAND DICTIONARY
    max_demand = sum(p for p in p_max_productions if p > 0) + sum(p_max_discharges) + sum(p_max_imposed) \
                 + max(min(flexi_dsm), -min(flexi_dsm))    # fixme: min is evaluated twice, max(x, -x) is abs
    min_demand = sum(p for p in p_min_productions if p < 0) + sum(p_max_charges) + sum(p_max_dissipation) \
                 - max(0, max(flexi_dsm))
    # else:
    #     max_demand = sum(p for p in p_max_productions if p > 0) + sum(p_max_imposed)
    #     min_demand = sum(p for p in p_min_productions if p < 0)
    #debug_print(min_demand, "Min power for demand dictionary")
    #debug_print(max_demand, "Max power for demand dictionary")
    demand_dict = build_demand_dictionary(max_range=max_demand, min_range=min_demand, step=multipurpose_step , Demand_file_name = Demand_file_name)
    # demand_dict = build_demand_dictionary(dictionary_struct_ranges, dsm_range, imposed_productions_max_powers)
    demand_range = list(demand_dict.keys())
    #debug_print(demand_range, "demand_range")
    # TODO: Adapt the length of the forbidden combinations list to the number of units at each calculation.

    for t, a in zip(task, approach):
        if t == "Distribution":
            # TODO: raise ValueError("One of the approaches was not recognized. You asked for {}, but only Structural
            #  or "Operational are available.".format(a))

            # DETERMINE FLEXIBILITY DISTRIBUTION(S) THROUGH THE REQUESTED APPROACH(ES)
            if a == "Structural":
                dict_struc_flexi = structural_flexibility_distribution(demand_dict, p_ranges_all_units)
                #debug_print(dict_struc_flexi, "structural flexibility dictionary")
                flexi_dist_all = list(dict_struc_flexi.values())
                dict_struc_flexi = structural_flexibility_distribution(demand_dict, p_ranges_prod_diss)
                flexi_dist_dissip = list(dict_struc_flexi.values())
                dict_struc_flexi = structural_flexibility_distribution(demand_dict, p_ranges_prods)
                flexi_dist_prod = list(dict_struc_flexi.values())
            elif a == "Operational":
                # flexi_dist_all = operational_flexibility_distribution(demand_dict, p_ranges_all_units, p_step_productions)
                flexi_dist_all = operational_flexibility_distribution(demand_dict, p_ranges_all_units, p_step_productions + p_step_dissipation + p_step_discharges)
                
                # flexi_dist_dissip = operational_flexibility_distribution(demand_dict, p_ranges_prod_diss, p_step_productions)
                
                flexi_dist_dissip = operational_flexibility_distribution(demand_dict, p_ranges_prod_diss, p_step_productions + p_step_dissipation)
                
                flexi_dist_prod = operational_flexibility_distribution(demand_dict, p_ranges_prods, p_step_productions)
                
            elif a == "Both":
                dict_struc_flexi, dict_oper_flexi = both_flexibility_distributions(demand_dict, p_ranges_all_units)
                flexi_dist_all = list(dict_oper_flexi.values())
                # flexi_dist_all = both_flexibility_distributions(demand_dict, p_ranges_all_units)
                dict_struc_flexi, dict_oper_flexi = both_flexibility_distributions(demand_dict, p_ranges_prod_diss)
                flexi_dist_dissip = list(dict_oper_flexi.values())
                flexi_dist_dissip = both_flexibility_distributions(demand_dict, p_ranges_prod_diss)
                dict_struc_flexi, dict_oper_flexi = both_flexibility_distributions(demand_dict, p_ranges_prods)
                flexi_dist_prod = list(dict_oper_flexi.values())
                flexi_dist_prod = both_flexibility_distributions(demand_dict, p_ranges_prods)
            else:
                raise ValueError("Sorry, the approach requested was not recognized: {}. It must be either Structural"
                                 "or Operational".format(a))
            plot_flexibility_distribution(a, demand_range, flexi_dist_all=flexi_dist_all, flexi_dsm=flexi_dsm,
                                          demand_dict=demand_dict, plotting_step=multipurpose_step , Demand_file_name =Demand_file_name)
            plot_flexibility_distribution(a, demand_range, flexi_dist_dissip=flexi_dist_dissip, flexi_dsm=flexi_dsm,
                                          demand_dict=demand_dict, plotting_step=multipurpose_step , Demand_file_name =Demand_file_name)
            plot_flexibility_distribution(a, demand_range, flexi_dist_prod=flexi_dist_prod, flexi_dsm=flexi_dsm,
                                          demand_dict=demand_dict, plotting_step=multipurpose_step , Demand_file_name =Demand_file_name)



            # MULTI-LAYER FLEXIBILITY DISTRIBUTION
            print("Starting 'while' loop.")
            # fixme: append --> + [0] * k
            while len(flexi_dist_prod) < len(flexi_dist_all):
                flexi_dist_prod.append(0)
            while len(flexi_dist_dissip) < len(flexi_dist_all):
                flexi_dist_dissip.append(0)

            if flexi_dist_prod and flexi_dist_dissip:
                # note: not Numpy native if not same length

                flexi_by_dissipation = [d - p for d, p in zip(flexi_dist_dissip, flexi_dist_prod)]
            else:
                flexi_by_dissipation = []
            # print("flexi_by_dissipation = {}".format(flexi_by_dissipation))  # For debug

            # print("flexi_dist_all = {}".format(flexi_dist_all))  # For debug
            # print("flexi_dist_dissip = {}".format(flexi_dist_dissip))  # For debug
            if flexi_dist_all and flexi_dist_dissip:
                flexi_by_storage = [t - d for t, d in zip(flexi_dist_all, flexi_dist_dissip)]
            else:
                flexi_by_storage = []
            # print("flexi_by_storage = {}".format(flexi_by_storage))  # For debug

            plot_flexibility_distribution(a, 
                                          demand_range, 
                                          flexi_dist_all = flexi_dist_all,
                                          flexi_dist_prod = flexi_dist_prod, 
                                          flexi_by_storage = flexi_by_storage,
                                          flexi_by_dissipation = flexi_by_dissipation, 
                                          flexi_dsm = flexi_dsm,
                                          demand_dict = demand_dict, 
                                          plotting_step = multipurpose_step,
                                          Demand_file_name =Demand_file_name)

            # debug_print(flexi_dist_prod, "flexi_dist_prod")
            # fig, ax = plt.subplots()
            # # ax.bar(list(demand_dict.keys()), flexi_dist_prod, color='g')  # To compare with demand
            # ax.bar(range(len(flexi_dist_prod)), flexi_dist_prod)
            # ax.set_title("Specific contribution of production units", weight='bold')
            # ax.set_ylabel("Additional flexibility", weight='bold')
            # ax.set_xlabel("Thermal power demand", weight='bold')

            # fig, ax = plt.subplots()
            # ax.bar(list(demand_dict.keys()), flexi_by_dissipation, color='r')
            # ax.set_title("Specific contribution of dissipation units", weight='bold')
            # ax.set_ylabel("Additional flexibility", weight='bold')
            # ax.set_xlabel("Thermal power demand", weight='bold')

            # ESTIMATION OF GLOBAL EFFECTIVE FLEXIBILITY VERSUS ANY DEMAND PROFILE (NON-CONSOLIDATED METHOD)
            # max_prod = sum([max(0, c) for c in p_max_piloted])
            # monte_carlo_estimation(flexi_dist_all, max_prod)
            # TODO: Calculate the specific contribution of each type of unit to flexibility
        else:
            # fixme: NotImplementedError more appropriate
            raise ValueError("The task named '{}' was not recognized. Only 'Distribution' is available.".format(t))

    # assess_effective_flexibility(dictionary_struct_ranges, demand_dict, imposed_productions_max_powers)

    print("Power demand = {}".format(demand))
    # print("Available max powers = {}".format(p_max_piloted))
    # print("Available min powers = {}".format(p_min_piloted))
    # print("Number of available units = {}".format(len(p_max_piloted)))
    # print("Maximal combined capacity = {}".format(sum(p_max_piloted)))
    toc_overall = time.time()  # Initialize clock # fixme wrong comment
    lapse_overall = toc_overall - tic_overall
    print("Total processing time: {}".format(lapse_overall))

    snapshot = tracemalloc.take_snapshot()
    top_stats = snapshot.statistics('lineno')
    print("[ Top 10 ]")
    for stat in top_stats[:10]:
        print(stat)

    plt.show()
    print("  ")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
    print("~~~ PROCESS HAS FINISHED. THANK YOU FOR USING THE FLEXIBILITY WIZARD ~~~")
    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")


# def build_demand_dictionary(dict_struct_ranges, range_dsm, imposed_prod):
def build_demand_dictionary(max_range, 
                            min_range, 
                            step,
                            Demand_file_name) :
    
    """ The demand dictionary counts how many time steps feature each power tranche in the demand profile. """
    print("\n")

    # min_range = max(max(dict_struct_ranges.values()))  # Initialize network min thermal power
    # max_range = 0  # Initialize network max thermal power
    # for i in dict_struct_ranges.values():  # Update min and max ranges through keys from structural dictionary
    #     for j in i:
    #         # print("Candidate {} was compared against {} for min power determination".format(j, min_range))  # Debug
    #         min_range = min(min_range, j)
    #         # print("Candidate {} was compared against {} for max power determination".format(j, max_range))  # Debug
    #         max_range = max(max_range, j)
    #
    # # debug_print(max(range_dsm), "max range dsm")
    # min_range += min(range_dsm)  # + sum(imposed_prod)  # Update min range with dsm contribution & imposed production
    # max_range += max(range_dsm)  # + sum(imposed_prod)  # Update max range with dsm contribution & imposed production
    # debug_print(min_range, "Minimal possible network power")  # For debug
    # debug_print(max_range, "Maximal possible network power")  # For debug
    # fixme: why are are min_range and max_range different from min (demand_series) and max(demand_series)
    demand_dict_keys = list(np.arange(min_range, max_range + 1, step=step))  # Set keys of demand load dictionary
    # TODO: Do max_range + 1/2 of the network's operating steps, instead of max_range + 1
    # fixme: 'demand_dict_keys[-1] > max_range' likely to happen if step < 1.
    # 'demand_dict_keys[-2] > max_range' will happe if 0<step<0.5, etc...
    if demand_dict_keys[-1] > max_range:  # Sometimes np.arange yields one too many increments. This loop clears that.
        del demand_dict_keys[-1]
    #debug_print(demand_dict_keys, "demand_dict_keys")  # For debug
    demand_dict_init_values = [0] * len(demand_dict_keys)  # Initialize values of demand load dictionary
    # debug_print(demand_dict_keys, "demand_dict_keys")
    # debug_print(demand_dict_init_values, "demand_dict_init_values")

    # fixme: see dict.fromkeys method
    dict_demand_load = dict(zip(demand_dict_keys, demand_dict_init_values))  # Initialize demand load dictionary


    # GENERATE LIST OF DEMAND INSTANCES FROM DEMAND FILE
    # fixme: use pathlib
    work_path = os.getcwd()
    # demand_file = open(work_path + "/demand_file.txt", "r")
    # fixme
    # demand_file = [(27+33)/2 + ((33-27)/2) * math.sin(2*k + (k**2)%3) for k in range(200)] #open(work_path + "/demand_file_illustrative_case.txt", "r")
    if Demand_file_name != None:
        demand_file = open(work_path + "/"+ Demand_file_name , "r")
        # fixme: list(map[...])
        demand_series = [c for c in map(float, demand_file)]
        # fixme: prefer Numpy conditionnal extraction.
        for d in demand_series[:]:  # This loop removes any demand over the network's maximal power, and warns the user.
            if d > max_range:
                warnings.warn(
                    "Warning: Your demand file contains a demand ({}) that exceeds the network's maximal power output"
                    " ({}). It was removed from the demand list.".format(d, max_range))
                demand_series.remove(d)
        # debug_print(dict_demand_load, "dict_demand_load")  # For debug
        # debug_print(demand_series, "demand_series")  # For debug
    
        # fixme: unsure of the role of these lines
        # 'key1 < d <= key2' instead of 'd in dict_demand_load.keys()'?
        for d in demand_series:
            if d in dict_demand_load.keys():
                dict_demand_load[d] += 1
            else:
                dict_demand_load[d] = 1  # TODO: If demand not in dictionary, not add it and warn the user


    #debug_print(dict_demand_load, "dict_demand_load")  # For debug

    # demand_file.close() # fixme

    # PLOT DEMAND LOAD DISTRIBUTION (Outdated since demand is plotted together with flexibility distributions)
    # fig, ax = plt.subplots()
    # debug_print(dict_demand_load, "dict_demand_load")
    # ax.plot(list(dict_demand_load.keys()), list(dict_demand_load.values()), color='k')
    # ax.set_title("Thermal demand load distribution", weight='bold')
    # ax.set_ylabel("Number of occurrences (time steps)", weight='bold')
    # ax.set_xlabel("Thermal power demand", weight='bold')

    return dict_demand_load



def structural_flexibility_distribution(dict_demand, p_range_all_units):
    """ This method scans every possible combination of energy units and their input/output powers, determines the
     network's net power for every combination, and records the demand tranches covered by each combination. """
     
    print("\n")
     
    #print(">> Determining structural flexibility distribution through new method.")
    #print("The list of power ranges is: {}".format(p_range_all_units))
    #print("And it is being compared against the following demand: {}".format(dict_demand))

    # fixme: useless with fromkeys. Use dict_demand instead
    list_demand = list(dict_demand.keys())  # Extract range of demand from the demand dictionary
    # fixme: see dict.fromkeys
    dict_struc_flexi = dict(zip(list_demand, [0] * len(list_demand)))  # Initialize structural flexibility dictionary
    dict_struc_flexi[0] += 1  # To take into account the possibility of not running any unit
    for demand in list_demand:
        for pick in range(1, len(p_range_all_units) + 1):
            """
            review notes: for an increasing number of units, determines the min total power and max total power
            """
            #print(">>  of {} unit(s) against demand = {}.".format(pick, demand))

            # Checking whether the demand escapes the combinations with minimal or maximal combined powers
            # fixme: probably useless copy
            choose_from = copy.deepcopy(p_range_all_units)
            # fixme: warning: lexicographic order is used if type(choose_from)=List[List]
            lowest_possible_power = sum([x[0] for x in heapq.nsmallest(pick, choose_from)])
            # fixme: do not reverse. Use key param of heapq.nlargest
            # fixme: could be stored outside of the loops
            [x.sort(reverse=True) for x in choose_from]
            highest_possible_power = sum([x[0] for x in heapq.nlargest(pick, choose_from)])
            if demand < lowest_possible_power or demand > highest_possible_power:
                #print(">> No configuration of {} unit(s) can cover a demand of {}.".format(pick, demand))
                #print(">> Skipping configurations of {} unit(s)".format(pick))
                continue
            if pick <= len(p_range_all_units)/2:
                symmetry = False
            else:
                symmetry = True
                pick = len(p_range_all_units) - pick  # Shortcut exploiting the symmetry of combinatorial distributions

            # note: symmetry exploit probably useless
            # 1) since time complexity related to the number of subsets (same for both pick and n-pick elements-per-subset)
            # 2) other kinds of symmetry might be hardcoded in itertools
            for structural_combination in itertools.combinations(p_range_all_units, pick):  # Scan every unit combination
                print("The inverse structural combination is: {}".format(structural_combination))
                print("The pick is: {}".format(pick))
                if symmetry is True:
                    inverse_choice = copy.deepcopy(p_range_all_units)
                    for p in structural_combination:
                        #print("The inverse structural combination is: {}".format(structural_combination))
                        # print("Removing this unit: {} from this list: {}".format(p, inverse_choice))
                        inverse_choice.remove(p)
                        # print("Inverse choice list after removal: {}".format(inverse_choice))
                        # print("p_ranges_all_units after removal: {}".format(p_ranges_all_units))
                    structural_combination = inverse_choice
                # fixme: if len(x)==2 and given sorted as parameters, replace with indexing (x[0], x[1])
                min_range = sum([min(x) for x in structural_combination])
                max_range = sum([max(x) for x in structural_combination])

                if demand < min_range or demand > max_range:
                    continue  # TODO: Should this rather be a 'pass'?
                else:
                    # print("Analyzing this structural combination: {}".format(structural_combination))
                    # TODO: Make sure that the structural combination does not contain user-forbidden units
                    # TODO: Include non-adjustable production of energy
                    # demand_not_covered = list_demand  # Keep track of demand tranches not covered
                    for operational_combination in itertools.product(*structural_combination):  # Scan every power combination
                        # print("Analyzing this operational combination: {}".format(operational_combination))
                        net_power = sum(operational_combination)
                        # print("The net power of this combination is: {}".format(net_power))
                        # print("The list of demand tranches not yet covered are: {}".format(demand_not_covered))
                        # what if 'demand' is in between (i.e. part-load necessary)?
                        # fixme: very unlikely to happen if net_power is int and demand is unconstrained float
                        # condition is met only for fake integer demands that were defined
                        if net_power == demand:
                            dict_struc_flexi[demand] += 1  # Operational flexibility increases with every valid combination
                            # print("This structural combination counted towards flexibility in demand = {}: {}".
                            #       format(demand, structural_combination))
                            break
                        # if net_power in demand_not_covered:
                        #     dict_struc_flexi[net_power] += 1  # Structural flexibility only increases by 1 for each combination
                        #     demand_not_covered.remove(net_power)  # That demand is covered at least once
                    # print("Finished analyzing this structural combination: {}".format(structural_combination))
    #print("Structural flexibility distribution: {}".format(list(dict_struc_flexi.values())))
    return dict_struc_flexi



def operational_flexibility_distribution(dict_demand, 
                                         operating_ranges_list, 
                                         p_step_productions):
    
    print("\n")
    
    #print(">> Started computing the operational flexibility distribution.")
    #print(">> The demand dictionary is: {}".format(dict_demand))
    #print(">> The list of operating ranges is: {}".format(operating_ranges_list))
    list_demand = list(dict_demand.keys())  # Extract range of demand from the demand dictionary
    # fixme: see dict.fromkeys
    dict_oper_flexi = dict(zip(list_demand, [0] * len(list_demand)))  # Initialize operational flexibility dictionary
    # fixme: copy is useless
    tuple_p_ranges_with_zeros = tuple(copy.deepcopy(operating_ranges_list))  # Create tuple deep copy of unit list
    #debug_print(tuple_p_ranges_with_zeros, "tuple_p_ranges_with_zeros")
    #debug_print(p_step_productions, "p_step_productions before append")
    p_ranges_with_zeros = []  # Initialize final list of power ranges with zeros in them
    # debug_print(tuple_p_ranges_with_zeros, "p_ranges_with_zeros before changes")
    while len(p_step_productions) < len(tuple_p_ranges_with_zeros):
        p_step_productions.append(1)
    #debug_print(p_step_productions, "p_step_productions after append")
    for x, y in zip(tuple_p_ranges_with_zeros, p_step_productions):
        # unit = list(copy.deepcopy(x))  # If disregarding operating steps at all
        # debug_print(x, "before bisect insort")
        #debug_print(y, "piloting step")
        min_pow = min(x)
        max_pow = max(x)
        #debug_print(min_pow, "min_pow")
        #debug_print(max_pow, "max_pow")
        # fixme: 'list' in 'list(np.[...])' is useless
        # fixme: why 'float'?
        unit = [round(float(c), 3) for c in list(np.arange(min_pow, max_pow + 0.75 * y, y))]  # TODO: This is assuming a step of 1, generalize for any step
        # debug_print(unit, "np.arange generated")
        if 0 not in unit:
            bisect.insort(unit, 0)
        # debug_print(unit, "bisect insort")
        p_ranges_with_zeros.append(unit)
    # debug_print(p_ranges_with_zeros, "p_ranges_with_zeros")
    operational_combinations = 1
    for item in p_ranges_with_zeros:
        operational_combinations *= len(item)
    #print(">> The list of units and operating ranges considered are: {}".format(p_ranges_with_zeros))
    #print(">> There are a total of {} operational combinations to be scanned.".format(operational_combinations))
    #print("Starting calculations...")
    progress_check = 0.01  # Check progress every 1%
    milestone = progress_check  # First milestone to be printed
    # b = len([i for i in itertools.product(*a) if sum(i) == 5])
    # for p in dict_oper_flexi.keys():
    #     dict_oper_flexi[p] = len([i for i in itertools.product(*a) if sum(i) == p])
    # for net_power in map(sum, itertools.product(*p_ranges_with_zeros)):
    #     dict_oper_flexi[net_power] += 1
    #debug_print(p_ranges_with_zeros, "p_ranges_with_zeros")
    for oper_combi in itertools.product(*p_ranges_with_zeros):  # Scan every combination of powers
        # fixme: why 'float'?
        net_power = round(float(sum(oper_combi)), 2)
        if net_power not in dict_oper_flexi:
            dict_oper_flexi[net_power] = 1
        else:
            dict_oper_flexi[net_power] += 1  # TODO: Failsafe in case the net power does not exist in the dictionary
        # fixme: 'list' is useless
        progress = sum(list(dict_oper_flexi.values())) / operational_combinations
        if progress > milestone:
            print("{} % of the operational combinations have been analyzed.".format(round(milestone*100, 10)))
            milestone += progress_check
    #debug_print(dict_oper_flexi, "dict_oper_flexi")
    mykeys = list(dict_oper_flexi.keys())
    mykeys.sort()
    # fixme: list is not needed. sorted_dict_oper_flexi = sorted(dict_oper_flexi.items())
    sorted_dict_oper_flexi = {i: dict_oper_flexi[i] for i in mykeys}
    #debug_print(sorted_dict_oper_flexi, "sorted_dict_oper_flexi")
    oper_flexibility_powers = list(sorted_dict_oper_flexi.keys())
    oper_flexibility_dist = list(sorted_dict_oper_flexi.values())
    #debug_print(oper_flexibility_powers, "oper_flexibility_powers")
    #debug_print(oper_flexibility_dist, "oper_flexibility_dist")
    plot_x = []
    plot_y = []
    key = -1
    # fixme: iterate over the dictionary using .items()
    # for key, value in oper_flexibility_dist.items():
    #     if value >0:
    #         plot_x.append(key)
    #         plot_y.append(value)
    for value in oper_flexibility_dist:
        key += 1
        if value > 0:
            plot_x.append(oper_flexibility_powers[key])
            plot_y.append(oper_flexibility_dist[key])
    #debug_print(plot_x, "plot_x")
    #debug_print(plot_y, "plot_y")
    # plt.bar(plot_x, plot_y, width=0.1)
    # plt.xticks(list(np.arange(min(oper_flexibility_powers), max(oper_flexibility_powers)+p_step_productions[0])), labels=None, rotation=-90)
    # plt.show()
    print("Total operational configurations: {}".format(sum(oper_flexibility_dist)))

    return oper_flexibility_dist



def both_flexibility_distributions(dict_demand, p_range_all_units):
    """ This method scans every possible combination of energy units and their input/output powers, determines the
     network's net power for every combination, and records the demand tranches covered by each combination. """
     
    print("\n")
     
    print(">> Determining flexibility distributions through the new method.")
    print("The list of power ranges is: {}".format(p_range_all_units))
    print("And it is being compared against the following demand: {}".format(dict_demand))

    # fixme: 'list' is useless, use dict.fromkeys()
    list_demand = list(dict_demand.keys())  # Extract range of demand from the demand dictionary
    dict_struc_flexi = dict(zip(list_demand, [0] * len(list_demand)))  # Initialize structural flexibility dictionary
    dict_oper_flexi = dict(zip(list_demand, [0] * len(list_demand)))  # Initialize operational flexibility dictionary
    for pick in range(1, len(p_range_all_units) + 1):
        print(">> Analyzing structural combinations of {} units.".format(pick))
        for structural_combination in itertools.combinations(p_range_all_units, pick):  # Scan every unit combination
            # print("Analyzing this structural combination: {}".format(structural_combination))
            # TODO: Make sure that the structural combination does not contain user-forbidden units
            # TODO: Include non-adjustable production of energy
            # demand_not_covered = list_demand  # Keep track of demand tranches not covered
            for operational_combination in itertools.product(*structural_combination):  # Scan every power combination
                # print("Analyzing this operational combination: {}".format(operational_combination))
                net_power = sum(operational_combination)
                # print("The net power of this combination is: {}".format(net_power))
                # print("The list of demand tranches not yet covered are: {}".format(demand_not_covered))
                # fixme: have you tried it? I think this raises KeyError if net_power not in list_demand
                dict_oper_flexi[net_power] += 1  # Operational flexibility increases with every valid combination
                # if net_power in demand_not_covered:
                #     dict_struc_flexi[net_power] += 1  # Structural flexibility only increases by 1 for each combination
                #     demand_not_covered.remove(net_power)  # That demand is covered at least once
            # print("Finished analyzing this structural combination: {}".format(structural_combination))
    print("Structural flexibility distribution: {}".format(list(dict_struc_flexi.values())))
    print("Operational flexibility distribution: {}".format(list(dict_oper_flexi.values())))
    return dict_struc_flexi, dict_oper_flexi



def assess_dsm_effects(demand_range: list = None, target_distribution: list = None, flexi_dsm: list = None,
                       default_label: str = 'With DSM', dsm_step=1):
    
    print("\n")
    
    # TODO: This function understands the DSM range as demand steps that one can displace over a flexibility
    #  distribution, but the rest of the functions, especially the one that builds the demand dictionary, understands
    #  the DSM range as power. Huge mismatch in the utilization of input data, that can easily break the program. Solve.

    tic_dsm_effects = time.time()  # Initialize clock
    print(">> Started assessing the effects of DSM on the flexibility distribution.")

    # fixme: initialize dsm_distribution with the exact number of elements it will contain, since you know this number  (len(target_distribution))
    dsm_distribution = []
    #debug_print(target_distribution, "target_distribution")
    # fixme: if p_dsm almost always equals 1, add a special 'if' to by pass division by one
    # fixme/warning: int(x) where x is a negative float negative is -int(-x), is it ok ?
    flexi_dsm = [int(p_dsm/dsm_step) for p_dsm in flexi_dsm]  # Convert DSM information from power to indices

    for c in range(len(target_distribution)):
        # fixme important: compute and store outside of the loop every variable that does not depend on 'c' (directly or indirectly)
        lower_index = max(0, c + min(0, int(min(flexi_dsm))))  # Maximal drop in demand list thanks to DSM
        upper_index = min(len(target_distribution) - 1, c + max(0, int(max(flexi_dsm))))  # Maximal increase in list
        dsm_range_index = np.arange(lower_index, upper_index + 1)  # Scan all indices touched by DSM
        dsm_range = [target_distribution[i] for i in dsm_range_index]  # Scan all distribution points touched by DSM
        lower_dsm_effect = target_distribution[c] - min(dsm_range)  # Maximal drop in flexibility due to DSM
        upper_dsm_effect = max(dsm_range) - target_distribution[c]  # Maximal increase in flexibility thanks to DSM
        local_dsm_effect = np.vstack([lower_dsm_effect, upper_dsm_effect])  # Record both DSM effects on that demand
        # fixme: since dsm_distribution is initialized (with 0), use dsm_distribution[c] = local_dsm_effect instead of append
        dsm_distribution.append(local_dsm_effect)  # Update array containing DSM effects demand by demand
        # debug_print(lower_index, "lower_index")
        # debug_print(upper_index, "upper_index")
        # debug_print(dsm_range_index, "dsm_range_index")
        # debug_print(dsm_range, "dsm_range")
        # debug_print(lower_dsm_effect, "lower_dsm_effect")
        # debug_print(upper_dsm_effect, "upper_dsm_effect")
        # debug_print(local_dsm_effect, "local_dsm_effect")

    for x in demand_range:
        label = default_label if x == 0 else None
        # fixme: compute and store outside of the loop every thing that does not depend on x
        # fixme: max(k, -k) is abs(k)
        y = int((x + max(demand_range[0], -demand_range[0])) / abs(demand_range[1] - demand_range[0]))
        # debug_print(demand_range, "demand_range")
        # debug_print(x, "x")
        # debug_print(y, "y")
        # debug_print(target_distribution, "in this list")
        # debug_print(len(target_distribution), "len(target_distribution)")
        # debug_print(dsm_distribution, "and in this list")
        # debug_print(len(dsm_distribution), "len(dsm_distribution)")
        plt.errorbar(x, target_distribution[y], yerr=dsm_distribution[y], fmt='o', color='k', label=label)

    toc_dsm_effects = time.time()  # Initialize clock
    lapse_dsm_effects = toc_dsm_effects - tic_dsm_effects
    print("DSM effects assessed successfully. Total computational time was {} seconds.".format(lapse_dsm_effects))

    return dsm_distribution



def plot_flexibility_distribution(approach, 
                                  demand_range, 
                                  flexi_dist_prod: list = None, 
                                  flexi_dist_store: list = None,
                                  flexi_dist_all: list = None, 
                                  flexi_dsm: list = None, 
                                  flexi_by_storage: list = None,
                                  flexi_by_dissipation: list = None, 
                                  flexi_dist_dissip: list = None,
                                  demand_dict: dict = None, 
                                  plotting_step: int = 1,
                                  Demand_file_name = None):
    
    print("\n")
    
    print(">> Started plotting {} flexibility distribution with the following lists of units:". format(approach))
    print("Production units: {}".format(flexi_dist_prod is not None))
    print("Dissipation units: {}".format(flexi_dist_dissip is not None))
    print("Storage units: {}".format(flexi_dist_store is not None))
    print("ALL units: {}".format(flexi_dist_all is not None))
    width = 0.9 * plotting_step  # bars width (default = 0.75): can also be len(x) sequence

    # if approach == "Operational":  # This is to try and calculate relative flexibility
    #     if flexi_dist_prod and flexi_dist_all:
    #         flexi_dist_prod = [c/max(flexi_dist_all) for c in flexi_dist_prod]
    #     if flexi_dist_store:
    #         flexi_dist_store = [c/max(flexi_dist_store) for c in flexi_dist_store]
    #     if flexi_dist_all:
    #         flexi_dist_all = [c/max(flexi_dist_all) for c in flexi_dist_all]
    #     if flexi_by_storage:
    #         flexi_by_storage = [c/max(flexi_dist_all) for c in flexi_by_storage]
    #     if flexi_by_dissipation:
    #         flexi_by_dissipation = [c/max(flexi_dist_all) for c in flexi_by_dissipation]

    fig, ax = plt.subplots()

    if flexi_dist_prod:
        # flexi_dist_prod = [c / max(flexi_dist_prod) for c in flexi_dist_prod]
        ax.bar(demand_range, flexi_dist_prod, width, color='g', label='Production')
        if flexi_by_dissipation:  # There are production, storage and dissipation units.
            ax.bar(demand_range, flexi_by_dissipation, width, color='r', label='+Dissipation',
                   bottom=flexi_dist_prod)
            if flexi_by_storage:
                ax.bar(demand_range, flexi_by_storage, width, color='darkorange', label='++Storage',
                       bottom=[p + d for p, d in zip(flexi_dist_prod, flexi_by_dissipation)])
                if flexi_dsm:
                    assess_dsm_effects(demand_range, flexi_dist_all, flexi_dsm, '+++DSM', dsm_step=plotting_step)
        elif flexi_by_storage:  # There are production and dissipation units.
            ax.bar(demand_range, flexi_by_storage, width, bottom=flexi_dist_prod, color='darkorange', label='+Storage')
            assess_dsm_effects(demand_range, flexi_dist_all, flexi_dsm, '+DSM', dsm_step=plotting_step)

        else:  # There are production units only.
            if flexi_dsm:
                assess_dsm_effects(demand_range, flexi_dist_prod, flexi_dsm, '+DSM', dsm_step=plotting_step)
    elif flexi_dist_store:  # There are production and storage units only.
        ax.bar(demand_range, flexi_dist_store, width, color='darkorange', label='Production + Storage')
        if flexi_dsm:
            assess_dsm_effects(demand_range, flexi_dist_store, flexi_dsm, '+DSM', dsm_step=plotting_step)
    elif flexi_dist_dissip:  # There are production and dissipation units only.
        ax.bar(demand_range, flexi_dist_dissip, width, color='r', label='Production + Dissipation')
        if flexi_dsm:
            assess_dsm_effects(demand_range, flexi_dist_dissip, flexi_dsm, '+DSM', dsm_step=plotting_step)
    elif flexi_dist_all:  # There are production, dissipation and storage units.
        #debug_print(demand_range, "demand_range")
        #debug_print(flexi_dist_all, "flexi_dist_all")
        ax.bar(demand_range, flexi_dist_all, width, color='darkorange', label='Production + Dissipation + Storage')
        if flexi_dsm:
            assess_dsm_effects(demand_range, flexi_dist_all, flexi_dsm, '+DSM', dsm_step=plotting_step)

    if Demand_file_name is not None:
        # set up the 2nd axis
        ax2 = ax.twinx()  # plot bar chart on axis #2
        #debug_print(demand_range, "demand range")  # For debug
        #debug_print(demand_dict.values(), "demand dict values")  # For debug
        # fixme: .values() is useless
        #debug_print(len(demand_dict.values()), "length demand dict values")  # For debug
        ax2.plot(demand_range, demand_dict.values(), color='b')
        ax2.grid(False)  # turn off grid #2
        ax2.set_ylabel('Demand frequency (time steps)', weight='bold')
        ax2.legend(['Demand'], loc="upper right")
        # ax2 = ax.twinx()
        # ax.plot(list(demand_dict.keys()), list(demand_dict.values()), color='m', label='demand', ax=ax2)

    # plt.yscale("log") if approach == "Operational" else plt.yscale("linear")
    # plt.yscale("log")
    # x_axis_steps = [c*max_demand/8 for c in list(range(9))]  # TODO: With this, x axis is sometimes difficult to read.
    # x_axis_steps = list(range(11)) * 0.1 * max_demand
    # x_axis_steps = range(0, (max_demand + 1))  # x ticks by steps of 1

    x_axis_steps = np.arange(min(demand_range), (max(demand_range) + 1), step=plotting_step)  # TODO: Adaptive steps
    plt.xticks(x_axis_steps, labels=None, rotation=-90)

    ax.set_ylabel("{} multiplicity".format(approach), weight='bold')
    ax.set_xlabel("Network's aggregated net power".format(approach), weight='bold')
    ax.set_title("{} multiplicity distribution".format(approach), weight='bold')
    ax.legend()
    # plt.savefig('Figure.png')


def assess_effective_flexibility(dict_struct_ranges, 
                                 dict_demand_load, 
                                 imposed_prod
                                 ):
    
    """ This method redistributes the demand among the possible configurations of the network. That leads to each
    configuration having a certain frequency (or probability) of existing due to the demand profile. """
    
    print("\n")

    # DETERMINE PROBABILITY DISTRIBUTION FOR THE NETWORK'S STRUCTURAL STATES
    dict_op_occurrences = dict()
    dict_op_probs = dict()
    dict_struct_occurrences = dict()
    dict_struct_probs = dict()
    excess_instances = 0  # Counter of additional instances artificially added for normalization purposes
    # fixme: use .items().
    #  e.g.: for d, frequency in dict_demand_load.items():
    for d in dict_demand_load.keys():  # Scan every power tranche in the demand dictionary
        frequency = dict_demand_load[d]  # Identify frequency (=no. of occurrences) of the power tranche
        # dict_op_probs[d] = frequency / sum(list(dict_demand_load.values()))  # Allocate operational probability
        # fixme: same than previous
        for s in dict_struct_ranges.keys():  # Scan every structural combination
            combined_range = dict_struct_ranges[s]  # Retrieve combined power range of the combination
            occurrences = combined_range.count(d)  # Count occurrences of the demand within that combination's range
            # print("The power tranche of {} has a total of {} demand instances and {} occurrences in this structural combination: {}"
            #       .format(d, frequency, occurrences, dict_struct_ranges[s]))
            struct_frequency = frequency * occurrences  # Allocate structural frequencies proportional to occurrences
            excess_instances += frequency * max(0, occurrences - 1)  # Keep track of additional instances given
            # print("excess_instances = {}".format(excess_instances))
            # fixme: .keys() is useless
            if s in dict_struct_occurrences.keys():
                dict_struct_occurrences[s] += struct_frequency  # Save data in structural dictionary
            else:
                dict_struct_occurrences[s] = struct_frequency  # Save data in structural dictionary
    sum_occurrences = sum(dict_struct_occurrences.values())
    # fixme: use .items()
    for s in dict_struct_occurrences.keys():
        dict_struct_probs[s] = dict_struct_occurrences[s] / sum_occurrences  # TODO: Prevent divisions by zero

    # DETERMINE PROBABILITY DISTRIBUTION FOR THE NETWORK'S OPERATIONAL STATES
    for s in dict_struct_occurrences.keys():  # Scan absolute frequency for every structural combination
        # fixme: list(..) and .keys() (both) are useless
        old_max_index = max(list(dict_op_occurrences.keys())) if dict_op_occurrences.keys() else 0
        for do in np.arange(1, len(dict_struct_ranges[s]) + 1):
            o = old_max_index + do  # Update index for updating operational dictionary
            # fixme: move outside of the loop what does not depend on 'do' (or 'o')
            dict_op_occurrences[o] = dict_struct_occurrences[s] / len(dict_struct_ranges[s])  # Allocate op. probs.
    for o in dict_op_occurrences.keys():
        dict_op_probs[o] = dict_op_occurrences[o] / sum(dict_op_occurrences.values())  # TODO: Prevent divisions by zero

    # THIS SECTION IS FOR DEBUGGING THE DISTRIBUTION OF DEMAND OCCURRENCES AMONG COMBINATIONS
    # print("This network has a total of {} possible operational states.".format(max(list(dict_op_probs.keys()))))
    # debug_print(dict_demand_load, "dict_demand_load")
    # print("A total of {} demand instances were distributed.".format(sum(list(dict_demand_load.values()))))
    # print("A total of {} excess instances were allocated.".format(excess_instances))
    # debug_print(dict_struct_occurrences, "dict_struct_occurrences")
    # debug_print(dict_struct_probs, "dict_struct_probs")
    # debug_print(dict_op_occurrences, "dict_op_occurrences")
    # debug_print(dict_op_probs, "dict_op_probs")
    # debug_print(sum(list(dict_struct_occurrences.values())), "sum of structural occurrences")
    # debug_print(sum(list(dict_op_occurrences.values())), "sum of operational occurrences")
    # debug_print(sum(list(dict_struct_probs.values())), "sum of structural probabilities")
    # debug_print(sum(list(dict_op_probs.values())), "sum of operational probabilities")

    effective_structural_flexibility = 0
    for prob in dict_struct_probs.values():
        if prob > 0:
            effective_structural_flexibility -= prob * np.log(prob)
    effective_operational_flexibility = 0
    for prob in dict_op_probs.values():
        if prob > 0:
            effective_operational_flexibility -= prob * np.log(prob)

    print("Your network's effective structural flexibility is: {}".format(effective_structural_flexibility))
    print("Your network's effective operational flexibility is: {}".format(effective_operational_flexibility))

    # PLOT PROBABILITY DISTRIBUTION FOR THE NETWORK'S STRUCTURAL STATES
    fig, ax = plt.subplots()
    width = 0.75  # the width of the bars: can also be len(x) sequence
    ax.bar(list(dict_struct_probs.keys()), list(dict_struct_probs.values()), width, color='r')
    ax.set_title("Probabilities for each network structural state", weight='bold')
    ax.set_ylabel("Probability of occurrence", weight='bold')
    ax.set_xlabel("Network's structural state (combination of units)", weight='bold')

    # PLOT PROBABILITY DISTRIBUTION FOR THE NETWORK'S OPERATIONAL STATES
    fig, ax = plt.subplots()
    width = 0.75  # the width of the bars: can also be len(x) sequence
    ax.bar(list(dict_op_probs.keys()), list(dict_op_probs.values()), width, color='r')
    ax.set_title("Probabilities for each operational state", weight='bold')
    ax.set_ylabel("Probability of occurrence", weight='bold')
    ax.set_xlabel("Network's operational state (combination of thermal powers)", weight='bold')



def debug_print(variable, name):
    """ Auxiliary method for quick-printing a variable that needs to be monitored for debug purposes. """
    print("Monitoring {} = {}".format(name, variable))



def find_in_list_of_list(mylist, char):
    """ Auxiliary method for finding a given element in a list of nested lists. """
    for sub_list in mylist:
        if char in sub_list:
            return mylist.index(sub_list), sub_list.index(char)
    raise ValueError("'{char}' is not in list".format(char = char))





