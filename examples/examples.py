from rocon.base_classes import arch
from rocon.fsm_class import fsm

def cntr_exmp():
    
    a0 = arch('IDLE', 'S1'  , 'valid = 1 and clear = 0            ', 'count = 1             ')
    a1 = arch('S1'  , 'S2'  , '(not valid = 0) and clear = 0      ', 'count = 2             ')
    a2 = arch('S2'  , 'S3'  , 'valid = 1 and (not clear = 1)      ', 'count = 3 and done = 1')
    a3 = arch('S3'  , 'S1'  , '(not valid = 0) and (not clear = 1)', 'count = 1             ')
    a4 = arch('S3'  , 'IDLE', 'clear = 1                          ', 'count = 0             ')
    a5 = arch('S2'  , 'IDLE', 'clear = 1                          ', 'count = 0             ')
    a6 = arch('S1'  , 'IDLE', 'clear = 1                          ', 'count = 0             ')
    
    return fsm([a0,a1,a2,a3,a4,a5,a6])

def cmp_exmp():

    a0 = arch('IDLE', 'S1'  , 'valid = erim and clear = aram                 ', 'count = 1             ')
    a1 = arch('S1'  , 'S2'  , 'not ((valid != erim) or (clear != aram))      ', 'count = 2             ')
    a2 = arch('S2'  , 'S3'  , 'valid = 1 and (not clear = 1)                 ', 'count = 3 and done = 1')
    a3 = arch('S3'  , 'S1'  , '(not valid = 0) and (not clear = 1)           ', 'count = 1             ')
    a4 = arch('S3'  , 'IDLE', 'clear = 1                                     ', 'count = 0             ')
    a5 = arch('S2'  , 'IDLE', 'clear = 1                                     ', 'count = 0             ')
    a6 = arch('S1'  , 'IDLE', 'clear = 1                                     ', 'count = 0             ')

    return fsm([a0,a1,a2,a3,a4,a5,a6])
