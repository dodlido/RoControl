from rocontrol.backend import * 

def get_counter():
    
    a0 = arch('IDLE', 'S1'  , 'vld = 1 and clr = 0', 'count = 1')
    a1 = arch('S1'  , 'S2'  , 'vld = 1 and clr = 0', 'count = 2')
    a2 = arch('S2'  , 'S3'  , 'vld = 1 and clr = 0', 'count = 3')
    a3 = arch('S3'  , 'S1'  , 'vld = 1 and clr = 0', 'count = 1')
    a4 = arch('S3'  , 'IDLE', 'clr = 1'            , 'count = 0')
    a5 = arch('S2'  , 'IDLE', 'clr = 1'            , 'count = 0')
    a6 = arch('S1'  , 'IDLE', 'clr = 1'            , 'count = 0')
    
    state_machine = fsm([a0,a1,a2,a3,a4,a5,a6])

    return state_machine
