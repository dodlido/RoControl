from rocontrol.roclass import * 

vld = input('vld', 1)
clr = input('clr', 1)

count = output('count', 2, 0)

idle = state('idle', True)
s1   = state('s1', False)
s2   = state('s2', False)
s3   = state('s3', False)

c_vld = condition(vld , 1, '=')
c_clr = condition(clr , 1, '=')

os0 = out_statement(count, 0)
os1 = out_statement(count, 1)
os2 = out_statement(count, 2)
os3 = out_statement(count, 3)

ei1  = edge(idle, s1, [c_vld, c_clr], ['& !', ''], [os1])

e12  = edge(s1, s2, [c_vld, c_clr], ['& !', ''], [os2])
e23  = edge(s2, s3, [c_vld, c_clr], ['& !', ''], [os3])
e31  = edge(s3, s1, [c_vld, c_clr], ['& !', ''], [os1])

e10  = edge(s1, idle, [c_clr], [''], [os0])
e20  = edge(s2, idle, [c_clr], [''], [os0])
e30  = edge(s3, idle, [c_clr], [''], [os0])

state_machine = fsm([vld, clr], [count], [ei1, e12, e23, e31, e10, e20, e30], [idle, s1, s2, s3])

state_machine.build_graph()

