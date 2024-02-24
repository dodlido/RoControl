##################################################################
#############         inferring.py                ################
# 1. Functions to help infer inputs, outpus and states from a ####
#    given arch list #############################################
##################################################################

# imports:
from typing import List, Tuple
from math import log2, ceil
from boolean_parser.actions.boolean import BoolNot, BoolAnd, BoolOr
from boolean_parser.actions.clause import Condition
from rocon.base_classes import input, output, state, arch

# Find the maximum value 'max' of a signaled named 'name' in condition 'cond'
def _get_max_val(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], name: str, max: int) -> int:
    if (isinstance(cond, Condition)): # Stopping condition
        if cond.value.isdigit(): 
            if (int(cond.value) > max) and (cond.name == name):
                return int(cond.value)
            else: 
                return max
        else: # Condition value is a different signal
            return max # Do not adjust max
    elif isinstance(cond, BoolNot): # Parse BoolNot
        return _get_max_val(cond.conditions[0], name, max)
    else: # Parse BoolAnd or BoolOr
        lhs_max = _get_max_val(cond.conditions[0], name, max)
        rhs_max = _get_max_val(cond.conditions[1], name, max)
        if lhs_max > rhs_max:
            return lhs_max 
        else:
            return rhs_max

def _get_rhs_names(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], rhs_names: List[str]=[]) -> List[str]:
    if (isinstance(cond, Condition)): # Stopping condition
        if not cond.value.isdigit():
            rhs_names.append(cond.value)
        return rhs_names
    elif isinstance(cond, BoolNot): # Parse BoolNot
        return _get_rhs_names(cond.conditions[0], rhs_names)
    else: # Parse BoolAnd or BoolOr
        lhs_list = _get_rhs_names(cond.conditions[0], rhs_names)
        rhs_list = _get_rhs_names(cond.conditions[1], rhs_names)
        joined_list= lhs_list + rhs_list
        return joined_list

def _find_missing_width(lhs_name: str, cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr]) -> str:
    if (isinstance(cond, Condition)): # Stopping condition
        if cond.name == lhs_name:
            return cond.value
        else:
            return ''
    elif isinstance(cond, BoolNot): # Parse BoolNot
        return _find_missing_width(lhs_name, cond.conditions[0])
    else: # Parse BoolAnd or BoolOr
        lhs_rhs = _find_missing_width(lhs_name, cond.conditions[0])
        rhs_rhs = _find_missing_width(lhs_name, cond.conditions[1])
        if lhs_rhs == '': # Currently supporting only a single appearance in cond
            return rhs_rhs 
        else:
            return lhs_rhs

# Parse through arch_list returning a list of conditions and a list of unique signal names (inputs or outputs based on get_out switch):
def _get_names_conds(arch_list: List[type[arch]], get_out: bool=False) -> Tuple[List[type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr]], List[str]]:
    names_list, cond_list = [], [] 
    for a in range(len(arch_list)):
        if get_out: # Find outputs in arch.out:
            if (isinstance(arch_list[a].out, Condition)):
                names_list.append(arch_list[a].out.name)
            else:
                names_list.extend(arch_list[a].out.params)
            cond_list.append(arch_list[a].out)
        else: # Find inputs in arch.cond:
            if (isinstance(arch_list[a].cond, Condition)):
                names_list.append(arch_list[a].cond.name)
            else:
                names_list.extend(arch_list[a].cond.params)
            cond_list.append(arch_list[a].cond)
        if not get_out:
            rhs_out_names = _get_rhs_names(arch_list[a].out)
            rhs_cond_names = _get_rhs_names(arch_list[a].cond)
            names_list += rhs_out_names + rhs_cond_names
    names_list = list(set(names_list)) # Unique names of all signals (outputs or inputs)
    return names_list, cond_list

def _get_widths(cond_list: List[type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr]], names_list: List[str]) -> List[int]:
    max_val_list, width_list, width_missing = [], [], []
    for i in range(len(names_list)):
        max_val_list.append(0)
    for i in range(len(names_list)): # Find maximum value for each signal for each condition:
        for j in range(len(cond_list)): 
            max_val_list[i] = _get_max_val(cond_list[j], names_list[i], max_val_list[i])
    for w in range(len(max_val_list)): # Assign width to each input based on maximum value:
        if (max_val_list[w]==0): # Signal not found in conditions or comapred to 0        
            curr_width = 1
            width_missing.append(w) 
        else: 
            curr_width = ceil(log2(max_val_list[w] + 1))
        width_list.append(curr_width)
    for w in width_missing: # Try to find missing widths:
        new_width = 1
        for cond in cond_list:
            rhs = _find_missing_width(names_list[w], cond) # Find name of signal on the right hand side of the signal with the missing width
            for name_ind, name in enumerate(names_list): # Go over all names and see if the rhs was assigned a different width
                if rhs==name and width_list[name_ind]>new_width: 
                    new_width = width_list[name_ind]>new_width
        width_list[w] = new_width
    return width_list

# Declare input or output base classes
def _get_inout_list(names_list, width_list, get_out: bool=False) -> List[input] | List[output]:
    inout_list = []
    for i in range(len(names_list)): # Define inputs or outputs class instances for each signal
        if get_out:
            inout_list.append(output(names_list[i], width_list[i], 0)) 
        else:
            inout_list.append(input(names_list[i], width_list[i]))
    return inout_list

# Returns a list of inputs or outputs depending on 'get_out' value from arch list
def get_fsm_interface(arch_list: List[type[arch]], get_out: bool=False) -> List[input] | List[output]:
    names_list, cond_list = _get_names_conds(arch_list, get_out) # Get names and conditions
    width_list = _get_widths(cond_list, names_list) # Get signal widths 
    return _get_inout_list(names_list, width_list, get_out) # Declare base classes

# Returns a tuple (default_state, list_of_states) for a given arch_list
def get_fsm_states(arch_list: List[arch], ds_name=None) -> Tuple[state, List[state]]:
    states = []
    state_names = []    
    final_state_list = []
    for i in range(len(arch_list)):
        if arch_list[i].source.name not in state_names: # Found new state in arch.source
            states.append(arch_list[i].source)
            state_names.append(arch_list[i].source.name)
        if arch_list[i].dest.name not in state_names: # Found new state in arch.dest
            states.append(arch_list[i].dest)
            state_names.append(arch_list[i].dest.name)
    if ds_name is None: # If default_state name is not specified, use first state
        states[0].reset=True
    else: # default state specified
        if ds_name in state_names: # this is the default state specified
            states[state_names.index(ds_name)].reset=True
        else:
            states.append(state(ds_name, True))
    reset_exists = False
    for s in states:
        if s.reset:
            default_state = s
            reset_exists = True
        else:
            final_state_list.append(s)
    if not reset_exists: # Specified state was not found in state list, use first state as default:
        states[0].reset=True
        print('Warning: Specified default state name was not found in state list, assigned first state as default')
        default_state = states[0]
        states.pop(0) # Remove default_state from state list
    return default_state, final_state_list