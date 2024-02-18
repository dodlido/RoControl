##################################################################
##############         build_graph.py            #################
# 1. helper functions to generate graph labels for fsm class #####
##################################################################

# imports:
from typing import List
from boolean_parser.actions.boolean import BoolNot, BoolAnd, BoolOr
from boolean_parser.actions.clause import Condition
from rocon.str_manipulation import lop_2_g
from rocon.base_classes import input, output

# Convert arch.cond to graph label
def cond_2_g(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]], label='') -> str:
    if (isinstance(cond, Condition)): # Stopping condition
        for s in sigs:
            if s.name == cond.name:
                w = s.width
        if w == 1: # Short version of writing is possible
            if cond.value == '1':
                return label + cond.name
            else:
                return label + '!' + cond.name
        else: # Full length writing is needed, signal's width is bigger than 1       
            return label + cond.name + cond.operator + cond.value
    elif isinstance(cond, BoolNot): # Parse BoolNot
        return label + lop_2_g(cond.logicop) + cond_2_g(cond.conditions[0], sigs, label)
    else: # Parse BoolAnd and BoolOr
        lhs = '(' + cond_2_g(cond.conditions[0], sigs, label) + ')'
        rhs = '(' + cond_2_g(cond.conditions[1], sigs, label) + ')'
        return label + lhs + lop_2_g(cond.logicop) + rhs

# Convert arch.out to graph label, returns a list contating each outputs assigned value
def out_2_g(cond: type[Condition]|type[BoolAnd], sigs: List[type[output]], out_list: List[int]) -> List[int]:
    if (isinstance(cond, Condition)): # Stopping condition
        for i, s in enumerate(sigs):
            if s.name==cond.name:
                out_list[i] = cond.value
        return out_list
    else: # Parse BoolAnd, no BoolNot or BoolOr allowed here
        left_list = out_2_g(cond.conditions[0], sigs, out_list)
        right_list = out_2_g(cond.conditions[1], sigs, out_list)
        for i in range(len(out_list)):
            if left_list[i] == -1: # Output not found to the left of the current position
                out_list[i] = right_list[i] # Assign value from the right side, even if it is -1
            else:
                out_list[i] = left_list[i]
        return out_list # This should contain -1 values for outputs not found in cond

# Wrapper function for out_2_g, converts the list of ints to a str which is the graph's output label for the specific cond
def out_2_g_wrapper(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[output]]) -> str:
    out_list = []
    for i in range(len(sigs)):
        out_list.append(-1) # Set initially to not found
    out_list = out_2_g(cond, sigs, out_list) # Try to find 'sigs' in 'cond' 
    label = '{'
    for i, o in enumerate(out_list):
        if o==-1: # If not found, assign default value
            label += str(sigs[i].default) + ', '
        else: # Assign found value
            label += str(o) + ', '
    return label[:-2] + '}'