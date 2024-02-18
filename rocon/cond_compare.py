##################################################################
#############         cond_compare.py                #############
# 1. Recursive function that drill bool_parser return values #####
#    and find if a condition is met for a given set of inputs ####
# 2. Wrapper functions to find if 2 conditions are equivalent ####
#    for any possible set of inputs ##############################
# 3. Wrapper functions to unite equivalent conditions in archs ###
##################################################################

# imports:
from typing import List
import itertools
from boolean_parser.actions.boolean import BoolNot, BoolAnd, BoolOr
from boolean_parser.actions.clause import Condition
from rocon.base_classes import input, output, arch
from rocon.str_manipulation import is_met_comp, is_met_lop

# Recursive function, bool return value indicates that recieved condition is met:
def check_cond(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]]|List[type[output]], values: List[int], truth: bool) -> bool:
    if (isinstance(cond, Condition)): # Stopping condition
        for i, s in enumerate(sigs):
            if s.name == cond.name:
                bottom_truth = is_met_comp(values[i], cond.operator, int(cond.value))
                return bottom_truth and truth
    elif isinstance(cond, BoolNot): # Parse BoolNot
        return not check_cond(cond.conditions[0], sigs, values, truth)
    else: # Parse BoolAnd or BoolOr
        lhs_truth = check_cond(cond.conditions[0], sigs, values, truth)
        rhs_truth = check_cond(cond.conditions[1], sigs, values, truth)
        return is_met_lop(lhs_truth, cond.logicop, rhs_truth)

# Checks if cond1 and cond2 are equivalent for a given set of inputs 'sigs' assigned a given set of values 'values'
def comp_conds(cond1: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr],
               cond2: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]], values: List[int]) -> bool:
    return check_cond(cond1, sigs, values, True)==check_cond(cond2, sigs, values, True)

# Returns a list of lists of ints containing all possible permutations of input list 'sigs'
def get_permuatations(sigs: List[type[input]]) -> List[List[int]]:
    biggest = 0
    max_val_list = []
    for sig in sigs:
        curr_max = int(pow(2, sig.width))
        max_val_list.append(curr_max-1)
        if biggest < curr_max:
            biggest = curr_max
    # Get all possible permutations, disregarding signal width:
    full_list = list(map(list, itertools.product(range(biggest), repeat=len(sigs)))) 
    # Append to better_list only items which are possible with regards to each signal's width
    better_list = []
    for i in range(len(full_list)):
        okay = True
        for s in range(len(sigs)):
            if full_list[i][s] > max_val_list[s]: # Exists an int in the current permutation which is too big
                okay = False
        if okay:
            better_list.append(full_list[i]) # If none violating elements found, append current to better_list
    return better_list

# Wrapper function to compare 'cond1' and 'cond2' for all possible inputs
def comp_conds_wrapper(cond1: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr],
                       cond2: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]]) -> bool:
    permutations = get_permuatations(sigs) # Returns all possible inputs
    equal = True
    for perm in permutations: # for each set of possible inputs, check if conditions are equal:
        if not comp_conds(cond1, cond2, sigs, perm):
            equal = False
    return equal

# Iterate over all conditions in arch_list, assign different ascending indices to different conditions
def unite_conds(arch_list: List[type[arch]], input_list: List[type[input]])->List[type[arch]]:
    index = 1
    for a1 in arch_list:
        if a1.index == 0 : # arch is still unlabeled
            a1.index = index # label with current index
            index += 1 
        for a2 in arch_list: # go over all other archs, label with same index if conditions are equivalent
            if a2.index==0:
                if comp_conds_wrapper(a1.cond, a2.cond, input_list):
                    a2.index = a1.index
    return arch_list