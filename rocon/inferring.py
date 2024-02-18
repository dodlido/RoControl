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
def get_max_val(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], name: str, max: int) -> int:
    if (isinstance(cond, Condition)): # Stopping condition
        if (int(cond.value) > max) and (cond.name == name):
            return int(cond.value)
        else:
            return max
    elif isinstance(cond, BoolNot): # Parse BoolNot
        return get_max_val(cond.conditions[0], name, max)
    else: # Parse BoolAnd or BoolOr
        lhs_max = get_max_val(cond.conditions[0], name, max)
        rhs_max = get_max_val(cond.conditions[1], name, max)
        if lhs_max > rhs_max:
            return lhs_max 
        else:
            return rhs_max

# Returns a list of inputs or outputs depending on 'get_out' value from arch list
def get_fsm_interface(arch_list: List[arch], get_out=False) -> List[input]|List[output]:
    names_list = []
    cond_list = []
    max_val_list = []
    width_list = []
    return_list = []
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
    names_list = list(set(names_list)) # Unique names of all signals (outputs or inputs)
    for i in range(len(names_list)):
        max_val_list.append(0)
    for i in range(len(names_list)): # Find maximum value for each signal for each condition:
        for a in range(len(arch_list)): 
            max_val_list[i] = get_max_val(cond_list[a], names_list[i], max_val_list[i])
    for w in range(len(max_val_list)): # Assign width to each input based on maximum value:
        if (max_val_list[w]==0):
            curr_width = 1 
        else: 
            curr_width = ceil(log2(max_val_list[w] + 1))
        width_list.append(curr_width)
    for i in range(len(names_list)): # Define inputs or outputs class instances for each signal
        if get_out:
            return_list.append(output(names_list[i], width_list[i], 0)) 
        else:
            return_list.append(input(names_list[i], width_list[i]))
    return return_list

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