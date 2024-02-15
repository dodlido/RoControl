from rocontrol.roclass import * 
from rocontrol import rocomp as COMP
from rocontrol import roperators as OP

def get_fsm():
    
    # Input decleration: 
    vld = input('vld', 1)
    clr = input('clr', 1)

    # Output decleration:
    count = output('count', 2, 0)

    # States decleration:
    idle = state('IDLE', True)
    s1   = state('S1', False)
    s2   = state('S2', False)
    s3   = state('S3', False)

    # Conditions decleration:
    c_vld = condition(vld, COMP.EQ, 1)
    c_clr = condition(clr, COMP.EQ, 1)
    c_inc = cond_list(c_vld, OP.AND, c_clr.invert(), OP.OR, 'erim=1\'b1')

    # Output statements decleration:
    os0 = out_statement(count, 0)
    os1 = out_statement(count, 1)
    os2 = out_statement(count, 2)
    os3 = out_statement(count, 3)

    # Transitions decleration:
    ei1  = edge(idle, s1, c_inc, [os1])
    e12  = edge(s1, s2, c_inc, [os2])
    e23  = edge(s2, s3, c_inc, [os3])
    e31  = edge(s3, s1, c_inc, [os1])
    e10  = edge(s1, idle, c_clr, [os0])
    e20  = edge(s2, idle, c_clr, [os0])
    e30  = edge(s3, idle, c_clr, [os0])

    # State machine constructor:
    state_machine = fsm([vld, clr], [count], [ei1, e12, e23, e31, e10, e20, e30], [idle, s1, s2, s3])

    return state_machine
