##################################################################
#############       str_manipulation.py               ############
# 1. String manipulation helper functions to convert paresd ######
#    values to verilog or graph labels ###########################
##################################################################

# Convert condition logical operation to verilog code:
def lop_2_v(lop: str) -> str:
    if lop=='or':
        return '||'
    elif lop=='and':
        return '&&'
    elif lop=='not':
        return '!'
    else:
        print('logical_op %s not supported yet', lop)
        exit(2)

# Convert condition logical operation to graph label:
def lop_2_g(lop: str) -> str:
    if lop=='or':
        return '|'
    elif lop=='and':
        return '&'
    elif lop=='not':
        return '!'
    else:
        print('logical_op %s not supported yet', lop)
        exit(2)

# Convert condition equal to verilog code:
def cop_2_v(cop: str) -> str:
    if cop=='=':
        return '=='
    else:
        return cop
    
# Return bool which indicates if 'Condition' is met (param op val) i.e (3 == 4)
def is_met_comp(param: int | str, op: str, val: int | str) -> bool:
    if op=='=':
        return param==val
    elif op=='!=':
        return param!=val
    elif op=='>':
        return param>val
    elif op=='>=':
        return param>=val
    elif op=='<=':
        return param<=val
    elif op=='<':
        return param<val
    else:
        print('logical_op %s not supported yet', op)
        exit(2)

# Return bool which indicates if BoolAnd, BoolNot, BoolOr are met:
def is_met_lop(b1: bool, lop: str, b2: bool) -> bool:
    if lop=='or':
        return b1 or b2
    elif lop=='and':
        return b1 and b2
    elif lop=='not':
        print('Not implemented yet') 
    else:
        print('logical_op %s not supported yet', lop)
        exit(2)