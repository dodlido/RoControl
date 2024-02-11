from rocontrol.roclass import * 

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
    c_vld = condition(vld , 1, '=')
    c_clr = condition(clr , 1, '=')

    # Output statements decleration:
    os0 = out_statement(count, 0)
    os1 = out_statement(count, 1)
    os2 = out_statement(count, 2)
    os3 = out_statement(count, 3)

    # Transitions decleration:
    ei1  = edge(idle, s1, [c_vld, c_clr], ['& !'], [os1])
    e12  = edge(s1, s2, [c_vld, c_clr], ['& !'], [os2])
    e23  = edge(s2, s3, [c_vld, c_clr], ['& !'], [os3])
    e31  = edge(s3, s1, [c_vld, c_clr], ['& !'], [os1])
    e10  = edge(s1, idle, [c_clr], [], [os0])
    e20  = edge(s2, idle, [c_clr], [], [os0])
    e30  = edge(s3, idle, [c_clr], [], [os0])

    # State machine constructor:
    state_machine = fsm([vld, clr], [count], [ei1, e12, e23, e31, e10, e20, e30], [idle, s1, s2, s3])

    return state_machine
