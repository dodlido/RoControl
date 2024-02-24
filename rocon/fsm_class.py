##################################################################
#############         fsm_class.py                ################
# 1. FSM class definition ########################################

##################################################################

# imports:
from typing import List, Tuple
import graphviz
from rocon.base_classes import input, output, state, arch
from rocon.build_graph import cond_2_g, out_2_g_wrapper
from rocon.build_verilog import get_verilog_header, get_verilog_footer, get_verilog_enum, get_verilog_interface, get_verilog_ns_logic, get_verilog_out_logic
from rocon.inferring import get_fsm_interface, get_fsm_states
from rocon.cond_compare import unite_conds

# FSM class:
class fsm:
    def __init__(self, arch_list: List[arch], default_state=None, clock=None, reset=None) -> None:
        self.graph     = graphviz.Digraph('FSM', filename='fsm.gv') # Create an empty directed graphviz graph
        self.inputs    = get_fsm_interface(arch_list)
        self.outputs   = get_fsm_interface(arch_list, get_out=True) 
        self.arch_list = unite_conds(arch_list, self.inputs)
        self.default_state, self.states = get_fsm_states(self.arch_list, default_state)
        if clock is None:
            self.clock     = input('clk', 1)
        else:
            self.clock     = input(clock, 1)
        if reset is None:
            self.reset     = input('rst_n', 1)
        else:
            self.reset     = input(reset, 1)

    # This functions builds self.graph using self.statets_list and self.edges_dict
    def build_graph(self, path) -> None:
        # Add entry:
        self.graph.node('', shape='point')
        self.graph.edge('', self.default_state.name, '!'+self.reset.name)
        # Add nodes:
        for state in self.states:
            self.graph.node(state.name)
        # Add edges:
        index_list, legend = [], 'Transitions:\n'
        for arch in self.arch_list:
            self.graph.edge(arch.source.name, arch.dest.name, (str(arch.index) + '\n' + out_2_g_wrapper(arch.out, self.outputs)))
            if arch.index not in index_list:
                index_list.append(arch.index)
                legend += str(arch.index) + ' --> ' + cond_2_g(arch.cond, self.inputs) + '\n'
        legend += '\nOutputs:\n{'
        for o in self.outputs:
            legend += o.name + ', '
        legend = legend[:-2] + '}'
        self.graph.node(legend, shape='box')
        # Render graph
        self.graph.render(path + '/ctrl.gv').replace('\\', '/')

    def build_verilog(self, path) -> None:
        code = ''
        # 0. Build module header:
        code += get_verilog_header()
        # 1. Build moudle interface:
        code += get_verilog_interface(self.clock, self.reset, self.inputs, self.outputs)
        # 2. Buile module enum and current state sample:
        code += get_verilog_enum(self.clock, self.reset, self.default_state, self.states)
        # 3. Build module next-state logic:
        code += get_verilog_ns_logic(self.inputs, [self.default_state] + self.states, self.arch_list)
        # 4. Build module output logic:
        code += get_verilog_out_logic(self.outputs, [self.default_state] + self.states, self.arch_list)
        # 5. Build module footer:
        code += get_verilog_footer()
        # 6. Write output .sv file:
        with open(path + '/ctrl.sv', 'w') as f:
            f.write(code) 