from boolean_parser import parse
from typing import List, Tuple
import graphviz
from datetime import datetime
from boolean_parser.actions.boolean import BoolNot, BoolAnd, BoolOr
from boolean_parser.actions.clause import Condition
from math import log2, ceil

# Classes:

# Input signal class:
class input:
    def __init__(self, name: str, width: int) -> None:
        self.name  = name  # input signal name
        self.width = width # input signal width in bits

# Output register class:
class output:
    def __init__(self, name: str, width: int, default: int) -> None:
        self.name    = name    # output signal name
        self.width   = width   # output signal width in bits
        self.default = default # output register default value

# State class:        
class state:
    def __init__(self, name: str, reset: bool) -> None:
        self.name  = name  # state name
        self.reset = reset # TRUE / FALSE: enter state @ reset

# Arch class:
class arch:
    def __init__ (self, source: type[state]|str, dest: type[state]|str, cond_str: str, out_str: str) -> None:
        if isinstance(source, str):
            self.source = state(source, False)
        else:
            self.source = source
        if isinstance(dest, str):
            self.dest = state(dest, False)
        else:
            self.dest = dest
        self.cond = parse(cond_str)
        self.out = parse(out_str)

# FSM helper functions:
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

def cop_2_v(cop: str) -> str:
    if cop=='=':
        return '=='
    else:
        return cop

def get_max_val(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], name: str, max: int) -> int:
    if (isinstance(cond, Condition)):
        if (int(cond.value) > max) and (cond.name == name):
            return int(cond.value)
        else:
            return max
    else:
        lhs_max = get_max_val(cond.conditions[0], name, max)
        rhs_max = get_max_val(cond.conditions[1], name, max)
    if lhs_max > rhs_max:
        return lhs_max 
    else:
        return rhs_max

def cond_2_v(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]]|List[type[output]], code='') -> str:
    if (isinstance(cond, Condition)):
        for s in sigs:
            if s.name == cond.name:
                w = s.width
        return code + cond.name + cop_2_v(cond.operator) + str(w) + '\'' + bin(int(cond.value))[1:]
    else:
        lhs = '(' + cond_2_v(cond.conditions[0], sigs, code) + ')'
        rhs = '(' + cond_2_v(cond.conditions[1], sigs, code) + ')'
        return code + lhs + lop_2_v(cond.logicop) + rhs
    
def cond_2_g(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]]|List[type[output]], label='') -> str:
    if (isinstance(cond, Condition)):
        for s in sigs:
            if s.name == cond.name:
                w = s.width
        if w == 1:
            if cond.value == '1':
                return label + cond.name
            else:
                return label + '!' + cond.name
        else:        
            return label + cond.name + cond.operator + cond.value
    else:
        lhs = '(' + cond_2_g(cond.conditions[0], sigs, label) + ')'
        rhs = '(' + cond_2_g(cond.conditions[1], sigs, label) + ')'
        return label + lhs + lop_2_g(cond.logicop) + rhs

def get_fsm_states(arch_list: List[arch], ds_name=None) -> Tuple[state, List[state]]:
    states = []
    state_names = []    
    final_state_list = []
    for i in range(len(arch_list)):
        if arch_list[i].source.name not in state_names:
            states.append(arch_list[i].source)
            state_names.append(arch_list[i].source.name)
        if arch_list[i].dest.name not in state_names:
            states.append(arch_list[i].dest)
            state_names.append(arch_list[i].dest.name)
    
    if ds_name is None:
        states[0].reset=True
    else:
        if ds_name in state_names:
            states[state_names.index(ds_name)].reset=True
        else:
            states.append(state(ds_name, True))
    
    for s in states:
        if s.reset:
            default_state = s
        else:
            final_state_list.append(s)

    return default_state, final_state_list

def get_fsm_interface(arch_list: List[arch], get_out=False) -> List[input]|List[output]:
    names_list = []
    cond_list = []
    max_val_list = []
    width_list = []
    return_list = []
    for a in range(len(arch_list)):
        if get_out:
            if (isinstance(arch_list[a].out, Condition)):
                names_list.append(arch_list[a].out.name)
            else:
                names_list.extend(arch_list[a].out.params)
            cond_list.append(arch_list[a].out)
        else:
            if (isinstance(arch_list[a].cond, Condition)):
                names_list.append(arch_list[a].cond.name)
            else:
                names_list.extend(arch_list[a].cond.params)
            cond_list.append(arch_list[a].cond)
    names_list = list(set(names_list)) # Remove duplicates
    for i in range(len(names_list)):
        max_val_list.append(0)
    for i in range(len(names_list)):
        for a in range(len(arch_list)):
            max_val_list[i] = get_max_val(cond_list[a], names_list[i], max_val_list[i])
    for w in range(len(max_val_list)):
        if (max_val_list[w]==0):
            curr_width = 1 
        else:
            curr_width = ceil(log2(max_val_list[w] + 1))
        width_list.append(curr_width)
    for i in range(len(names_list)):
        if get_out:
            return_list.append(output(names_list[i], width_list[i], 0)) # TODO: think about how to propogate default value
        else:
            return_list.append(input(names_list[i], width_list[i]))
    return return_list

# FSM class:
class fsm:
    def __init__(self, arch_list: List[arch], default_state=None, clock=None, reset=None) -> None:
        self.graph     = graphviz.Digraph('FSM', filename='fsm.gv') # Create an empty directed graphviz graph
        self.arch_list = arch_list
        self.inputs    = get_fsm_interface(self.arch_list)
        self.outputs   = get_fsm_interface(self.arch_list, get_out=True) 
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
        for arch in self.arch_list:
            self.graph.edge(arch.source.name, arch.dest.name, (cond_2_g(arch.cond, self.inputs) + '\n{' + cond_2_g(arch.out, self.outputs) + '}'))
        # Render graph
        self.graph.render(path + '/ctrl.gv').replace('\\', '/')

    def build_verilog(self, path) -> None:
        code = ''
        # 0. Build module header:
        code += self.get_verilog_header()
        # 1. Build moudle interface:
        code += self.get_verilog_interface()
        # 2. Buile module enum and current state sample:
        code += self.get_verilog_enum()
        # 3. Build module next-state logic:
        code += self.get_verilog_ns_logic()
        # 4. Build module output logic:
        code += self.get_verilog_out_logic()
        # 5. Build module footer:
        code += self.get_verilog_footer()
        # 6. Write output .sv file:
        with open(path + '/ctrl.sv', 'w') as f:
            f.write(code) 
    
    def get_verilog_header(self) -> str:
        date    = datetime.today().strftime('%Y-%m-%d')
        header  =     '//| Name: ctrl.sv                            |//\n'
        header +=     '//| Date: '+ date +'                         |//\n'
        header +=     '//| Description: Automatically generated FSM |//\n'
        header +=     '//| Generated using RoControl python package |//\n'
        header +=     '                                                \n'
        header +=     'module ctrl #() (                               \n'
        return header + '\n'
    
    def get_verilog_interface(self) -> str:
        interface = ''
        interface += '   input wire [' + str(self.clock.width-1) + ':0] ' + self.clock.name + ',\n'
        interface += '   input wire [' + str(self.reset.width-1) + ':0] ' + self.reset.name + ',\n'
        for i in range(len(self.inputs)):
            interface += '   input wire [' + str(self.inputs[i].width-1) + ':0] ' + self.inputs[i].name + ',\n'
        for i in range(len(self.outputs)):
            interface += '   output reg [' + str(self.outputs[i].width-1) + ':0] ' + self.outputs[i].name + ',\n'
        interface = interface[:-2] + '\n);\n' # Remove final comma and add ); at the end
        return interface + '\n'
    
    def get_verilog_enum(self) -> str:
        enum = 'typedef enum {\n'
        for i in range(len(self.states)):
            enum += '   ' + self.states[i].name + ',\n'
        enum += '} State ;\n'
        enum += 'State current_state, next_state ;\n'
        enum += 'always_ff @(posedge ' + self.clock.name + ', negedge ' + self.reset.name + ') begin\n'
        enum += '   if (!' + self.reset.name + ')\n'
        enum += '      current_state <= ' + self.default_state.name + ' ;\n'
        enum += '   else\n'
        enum += '      current_state <= next_state ;\n'
        enum += 'end\n'
        return enum + '\n'

    def get_verilog_ns_logic(self) -> str:
        ns_logic  = 'always_comb begin\n'
        ns_logic += '   case(current_state)\n'
        for s in self.states:
            a_list = []
            for a in self.arch_list: 
                if a.source.name == s.name:
                    a_list.append(a)
            if len(a_list)==0:
                continue
            else:
                ns_logic += '      ' + s.name + ': begin\n'
                ns_logic += '         if ' + cond_2_v(a_list[0].cond, self.inputs) + '\n'
                ns_logic += '            next_state = ' + a_list[0].dest.name + ';\n'
                for i in range(len(a_list)):
                    if i != 0:
                        ns_logic += '         else if ' + cond_2_v(a_list[i].cond, self.inputs) + '\n'
                        ns_logic += '            next_state = ' + a_list[i].dest.name + ';\n'
                ns_logic += '         else\n'
                ns_logic += '            next_state = ' + s.name + ';\n'
            ns_logic += '      end\n'
        ns_logic += '   endcase\n'
        ns_logic += 'end\n'
        return ns_logic + '\n'
    
    def get_verilog_out_logic(self) -> str:
        out_logic  = 'always_comb begin\n'
        for o in self.outputs:
            out_logic += '   ' + o.name + ' = ' + str(o.width) + '\'' + bin(o.default)[1:] + ' ;\n'
        out_logic += '   case(current_state)\n'
        for s in self.states:
            out_logic += '      ' + s.name + ': begin\n'
            for a in self.arch_list: 
                if a.source.name == s.name:
                    out_logic += '         if (next_state == ' + a.dest.name + ')\n'
                    out_logic += '            ' + cond_2_v(a.out, self.outputs) + ';\n'
            out_logic += '      ' + 'end\n'
        out_logic += '   endcase\n'
        out_logic += 'end\n'
        
        return out_logic + '\n'
        
    def get_verilog_footer(self) -> str:
        footer  = 'endmodule:ctrl\n\n'
        footer += '//| Enjoy! Esty                                  |//\n'
        return footer

