##################################################################
#############         build_verilog.py            ################
# 1. helper functions to generate verilog code for fsm class #####
##################################################################

# imports:
from datetime import datetime
from typing import List
from boolean_parser.actions.boolean import BoolNot, BoolAnd, BoolOr
from boolean_parser.actions.clause import Condition
from rocon.str_manipulation import cop_2_v, lop_2_v
from rocon.base_classes import input, output, state, arch

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

def get_verilog_header() -> str:
    date    = datetime.today().strftime('%Y-%m-%d')
    header  =     '//| Name: ctrl.sv                            |//\n'
    header +=     '//| Date: '+ date +'                         |//\n'
    header +=     '//| Description: Automatically generated FSM |//\n'
    header +=     '//| Generated using RoControl python package |//\n'
    header +=     '                                                \n'
    header +=     'module ctrl #() (                               \n'
    return header + '\n'

def get_verilog_interface(clock: input, reset: input, inputs: List[input], outputs: List[output]) -> str:
    interface = ''
    interface += '   input wire [' + str(clock.width-1) + ':0] ' + clock.name + ',\n'
    interface += '   input wire [' + str(reset.width-1) + ':0] ' + reset.name + ',\n'
    for i in range(len(inputs)):
        interface += '   input wire [' + str(inputs[i].width-1) + ':0] ' + inputs[i].name + ',\n'
    for i in range(len(outputs)):
        interface += '   output reg [' + str(outputs[i].width-1) + ':0] ' + outputs[i].name + ',\n'
    interface = interface[:-2] + '\n);\n' # Remove final comma and add ); at the end
    return interface + '\n'

def get_verilog_enum(clock: input, reset: input, default_state: state, states: List[state]) -> str:
    enum = 'typedef enum {\n   ' + default_state.name + ',\n'
    for i in range(len(states)):
        enum += '   ' + states[i].name + ',\n'
    enum += '} State ;\n'
    enum += 'State current_state, next_state ;\n'
    enum += 'always_ff @(posedge ' + clock.name + ', negedge ' + reset.name + ') begin\n'
    enum += '   if (!' + reset.name + ')\n'
    enum += '      current_state <= ' + default_state.name + ' ;\n'
    enum += '   else\n'
    enum += '      current_state <= next_state ;\n'
    enum += 'end\n'
    return enum + '\n'

def get_verilog_ns_logic(inputs: List[input], states: List[state], archs: List[arch]) -> str:
    ns_logic  = 'always_comb begin\n'
    ns_logic += '   case(current_state)\n'
    for s in states:
        a_list = []
        for a in archs: 
            if a.source.name == s.name:
                a_list.append(a)
        if len(a_list)==0:
            continue
        else:
            ns_logic += '      ' + s.name + ': begin\n'
            ns_logic += '         if ' + cond_2_v(a_list[0].cond, inputs) + '\n'
            ns_logic += '            next_state = ' + a_list[0].dest.name + ';\n'
            for i in range(len(a_list)):
                if i != 0:
                    ns_logic += '         else if ' + cond_2_v(a_list[i].cond, inputs) + '\n'
                    ns_logic += '            next_state = ' + a_list[i].dest.name + ';\n'
            ns_logic += '         else\n'
            ns_logic += '            next_state = ' + s.name + ';\n'
        ns_logic += '      end\n'
    ns_logic += '   endcase\n'
    ns_logic += 'end\n'
    return ns_logic + '\n'

def get_verilog_out_logic(outputs: List[output], states: List[state], archs: List[arch]) -> str:
    out_logic  = 'always_comb begin\n'
    for o in outputs:
        out_logic += '   ' + o.name + ' = ' + str(o.width) + '\'' + bin(o.default)[1:] + ' ;\n'
    out_logic += '   case(current_state)\n'
    for s in states:
        out_logic += '      ' + s.name + ': begin\n'
        for a in archs: 
            if a.source.name == s.name:
                out_logic += '         if (next_state == ' + a.dest.name + ')\n'
                out_logic += '            ' + out_2_v_wrapper(a.out, outputs)
        out_logic += '      ' + 'end\n'
    out_logic += '   endcase\n'
    out_logic += 'end\n'
    
    return out_logic + '\n'
    
def get_verilog_footer() -> str:
    footer  = 'endmodule:ctrl\n\n'
    footer += '//| Enjoy! Esty                                  |//\n'
    return footer