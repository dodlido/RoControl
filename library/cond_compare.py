##################################################################
#############         cond_compare.py                #############
# 1. Recursive function that drill bool_parser return values #####
#    and find if a condition is met for a given set of inputs ####
# 2. Wrapper functions to find if 2 conditions are equivalent ####
#    for any possible set of inputs ##############################
# 3. Wrapper functions to unite equivalent conditions in archs ###
##################################################################

# imports:
from typing import List, Tuple
import itertools
from boolean_parser.actions.boolean import BoolNot, BoolAnd, BoolOr
from boolean_parser.actions.clause import Condition
from rocon.base_classes import input, output, arch
from rocon.str_manipulation import is_met_comp, is_met_lop

# Recursive function, bool return value indicates that recieved condition is met:
def _check_cond_dig(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr],
                     sigs: List[type[input]]|List[type[output]], values: List[int], truth: bool=False, ignore: bool=False) -> Tuple[bool, bool]:
    if (isinstance(cond, Condition)): # Stopping condition
        for i, s in enumerate(sigs):
            if s.name == cond.name:
                if cond.value.isdigit():
                    bottom_truth = is_met_comp(values[i], cond.operator, int(cond.value))
                    return (bottom_truth and truth, False)
                else: # Signal is not comapred to a number but to some unknown value
                    return (truth, True)
    elif isinstance(cond, BoolNot): # Parse BoolNot
        (ds_truth, ds_ignore) = _check_cond_dig(cond.conditions[0], sigs, values, truth)
        if ds_ignore:
            return (True, False)
        else:
            return (ds_truth, False)
    else: # Parse BoolAnd or BoolOr
        (lhs_truth, lhs_ignore) = _check_cond_dig(cond.conditions[0], sigs, values, truth)
        (rhs_truth, rhs_ignore) = _check_cond_dig(cond.conditions[1], sigs, values, truth)
        if lhs_ignore and rhs_ignore:
            return (is_met_lop(True, cond.logicop, True), False)
        elif lhs_ignore and not rhs_ignore:
            return (is_met_lop(True, cond.logicop, rhs_truth), False)
        elif not lhs_ignore and rhs_ignore:
            return (is_met_lop(lhs_truth, cond.logicop, True), False)
        else:
            return (is_met_lop(lhs_truth, cond.logicop, rhs_truth), False)

# Recursive function, bool return value indicates that recieved condition is met:
def _check_cond_str(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr],
                     sigs: List[type[input]]|List[type[output]], values: List[str], truth: bool=False, ignore: bool=False) -> Tuple[bool, bool]:
    if (isinstance(cond, Condition)): # Stopping condition
        for i, s in enumerate(sigs):
            if s.name == cond.name:
                if cond.value.isdigit(): # This is checked in _dig twin function
                    return (truth, True)
                else: # Signal is not comapred to a number but to some input signal
                    bottom_truth = is_met_comp(values[i], cond.operator, cond.value)
                    return (bottom_truth and truth, False)
    elif isinstance(cond, BoolNot): # Parse BoolNot
        (ds_truth, ds_ignore) = _check_cond_str(cond.conditions[0], sigs, values, truth)
        if ds_ignore:
            return (True, False)
        else:
            return (ds_truth, False)
    else: # Parse BoolAnd or BoolOr
        (lhs_truth, lhs_ignore) = _check_cond_str(cond.conditions[0], sigs, values, truth)
        (rhs_truth, rhs_ignore) = _check_cond_str(cond.conditions[1], sigs, values, truth)
        if lhs_ignore and rhs_ignore:
            return (is_met_lop(True, cond.logicop, True), False)
        elif lhs_ignore and not rhs_ignore:
            return (is_met_lop(True, cond.logicop, rhs_truth), False)
        elif not lhs_ignore and rhs_ignore:
            return (is_met_lop(lhs_truth, cond.logicop, True), False)
        else:
            return (is_met_lop(lhs_truth, cond.logicop, rhs_truth), False)

# Checks if cond1 and cond2 are equivalent for a given set of inputs 'sigs' assigned a given set of values 'values'
def _comp_conds_dig(cond1: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr],
               cond2: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]], values: List[int]) -> bool:
    (eq1, _) = _check_cond_dig(cond1, sigs, values)
    (eq2, _) = _check_cond_dig(cond2, sigs, values)
    return eq1==eq2
# Checks if cond1 and cond2 are equivalent for a given set of inputs 'sigs' assigned a given set of input signal names
def _comp_conds_str(cond1: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr],
               cond2: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]], values: List[str]) -> bool:
    (eq1, _) = _check_cond_str(cond1, sigs, values)
    (eq2, _) = _check_cond_str(cond2, sigs, values)
    return eq1==eq2

# Returns a list of lists of ints containing all possible permutations of input list 'sigs'
def _get_permuatations_dig(sigs: List[type[input]]) -> List[List[int]]:
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

# Return all permutations of signal names list
def _get_permutations_str(sigs: List[type[input]]) -> List[List[str]]:
    names = []
    for s in sigs:
        names.append(s.name)
    return list(itertools.permutations(names))

# Wrapper function to compare 'cond1' and 'cond2' for all possible inputs
def _comp_conds_wrapper(cond1: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr],
                       cond2: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]]) -> bool:
    permutations_dig = _get_permuatations_dig(sigs) # Returns all possible input values
    permutations_str = _get_permutations_str(sigs) # Return all permutations of input signal names
    equal = True
    for perm in permutations_dig: # for each set of possible inputs, check if conditions are equal:
        if not _comp_conds_dig(cond1, cond2, sigs, perm):
            equal = False
    for perm in permutations_str:
        if not _comp_conds_str(cond1, cond2, sigs, perm):
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
                if _comp_conds_wrapper(a1.cond, a2.cond, input_list):
                    a2.index = a1.index
    return arch_list