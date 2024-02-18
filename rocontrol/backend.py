from boolean_parser import parse
from typing import List, Tuple
import graphviz
from datetime import datetime
from boolean_parser.actions.boolean import BoolNot, BoolAnd, BoolOr
from boolean_parser.actions.clause import Condition
from math import log2, ceil, pow
import itertools

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
    def __init__ (self, source: type[state]|str, dest: type[state]|str, cond_str: str, out_str: str, index=0) -> None:
        if isinstance(source, str):
            self.source = state(source, False)
        else:
            self.source = source
        if isinstance(dest, str):
            self.dest = state(dest, False)
        else:
            self.dest = dest
        self.index = index
        self.cond = parse(cond_str)
        self.out = parse(out_str)

# FSM helper functions:
        
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

# Return bool which indicates if 'Condition' is met (param op val) i.e (3 == 4)
def is_met_comp(param: int, op: str, val: int) -> bool:
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

# Recursive function, bool return value indicates that recieved condition is met:
def check_cond(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]]|List[type[output]], values: List[int], truth: bool) -> bool:
    if (isinstance(cond, Condition)): # Stopping condition
        for i, s in enumerate(sigs):
            if s.name == cond.name:
                bottom_truth = is_met_comp(values[i], cond.operator, int(cond.value))
                return bottom_truth and truth
    elif isinstance(cond, BoolNot): # Parse BoolNot
        return not check_cond(cond.conditions[0], sigs, values, truth)
    else: # Parse BoolAnd or BoolOr
        lhs_truth = check_cond(cond.conditions[0], sigs, values, truth)
        rhs_truth = check_cond(cond.conditions[1], sigs, values, truth)
        return is_met_lop(lhs_truth, cond.logicop, rhs_truth)

# Checks if cond1 and cond2 are equivalent for a given set of inputs 'sigs' assigned a given set of values 'values'
def comp_conds(cond1: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr],
               cond2: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]], values: List[int]) -> bool:
    return check_cond(cond1, sigs, values, True)==check_cond(cond2, sigs, values, True)

# Returns a list of lists of ints containing all possible permutations of input list 'sigs'
def get_permuatations(sigs: List[type[input]]) -> List[List[int]]:
    biggest = 0
    max_val_list = []
    for sig in sigs:
        curr_max = int(pow(2, sig.width))
        max_val_list.append(curr_max-1)
        if biggest < curr_max:
            biggest = curr_max
    # Get all possible permutations, disregarding signal width:
    full_list = list(map(list, itertools.product(range(biggest), repeat=len(sigs)))) 
    # Append to better_list only items which are possible with regards to each signal's width
    better_list = []
    for i in range(len(full_list)):
        okay = True
        for s in range(len(sigs)):
            if full_list[i][s] > max_val_list[s]: # Exists an int in the current permutation which is too big
                okay = False
        if okay:
            better_list.append(full_list[i]) # If none violating elements found, append current to better_list
    return better_list

# Wrapper function to compare 'cond1' and 'cond2' for all possible inputs
def comp_conds_wrapper(cond1: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr],
                       cond2: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]]) -> bool:
    permutations = get_permuatations(sigs) # Returns all possible inputs
    equal = True
    for perm in permutations: # for each set of possible inputs, check if conditions are equal:
        if not comp_conds(cond1, cond2, sigs, perm):
            equal = False
    return equal

# Iterate over all conditions in arch_list, assign different ascending indices to different conditions
def unite_conds(arch_list: List[type[arch]], input_list: List[type[input]])->List[type[arch]]:
    index = 1
    for a1 in arch_list:
        if a1.index == 0 : # arch is still unlabeled
            a1.index = index # label with current index
            index += 1 
        for a2 in arch_list: # go over all other archs, label with same index if conditions are equivalent
            if a2.index==0:
                if comp_conds_wrapper(a1.cond, a2.cond, input_list):
                    a2.index = a1.index
    return arch_list

# Convert arch.cond to verilog code
def cond_2_v(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[input]]|List[type[output]], code='') -> str:
    if (isinstance(cond, Condition)): # Stopping condition
        for s in sigs:
            if s.name == cond.name:
                w = s.width
        return code + cond.name + cop_2_v(cond.operator) + str(w) + '\'' + bin(int(cond.value))[1:]
    elif isinstance(cond, BoolNot): # Parse BoolNot
        return code + lop_2_v(cond.logicop) + cond_2_v(cond.conditions[0], sigs, code)
    else: # Parse BoolAnd and BoolOr
        lhs = '(' + cond_2_v(cond.conditions[0], sigs, code) + ')'
        rhs = '(' + cond_2_v(cond.conditions[1], sigs, code) + ')'
        return code + lhs + lop_2_v(cond.logicop) + rhs

# Convert arch.out to verilog code
def out_2_v(cond: type[Condition]|type[BoolAnd], sigs: List[type[output]], code='') -> str:
    if (isinstance(cond, Condition)): # Stopping condition
        for s in sigs:
            if s.name == cond.name:
                w = s.width
        return code + cond.name + cop_2_v(cond.operator) + str(w) + '\'' + bin(int(cond.value))[1:] + ';\n'
    else: # Parse BoolAnd, no BoolOr or BoolNot are allowed in arch.out
        lhs = out_2_v(cond.conditions[0], sigs, code)
        rhs = out_2_v(cond.conditions[1], sigs, code)
        return code + lhs + rhs

# Wrapper function to recursive out_2_v, used to fix ident issues with multiple outputs
def out_2_v_wrapper(cond: type[Condition]|type[BoolAnd]|type[BoolNot]|type[BoolOr], sigs: List[type[output]]) -> str:
    pre_code = out_2_v(cond, sigs, '')
    post_code = ''
    for c in pre_code:
        if c=='\n': # Multiple outputs
            post_code += c + '            ' # Manual ident fixe
        else:
            post_code += c
    return post_code[:-12] # Undo last output ident fix

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
            # self.graph.edge(arch.source.name, arch.dest.name, (cond_2_g(arch.cond, self.inputs) + '\n{' + cond_2_g(arch.out, self.outputs) + '}'))
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
                    out_logic += '            ' + out_2_v_wrapper(a.out, self.outputs)
            out_logic += '      ' + 'end\n'
        out_logic += '   endcase\n'
        out_logic += 'end\n'
        
        return out_logic + '\n'
        
    def get_verilog_footer(self) -> str:
        footer  = 'endmodule:ctrl\n\n'
        footer += '//| Enjoy! Esty                                  |//\n'
        return footer