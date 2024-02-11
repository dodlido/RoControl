import graphviz
from typing import List, Union
from datetime import datetime

# Input signal class:
class input:

    def __init__(self, name: str, width: int, type=None) -> None:
        self.name  = name  # input signal name
        self.width = width # input signal width in bits
        self.type  = type  # clock / reset / regular (None, Default)

# Output register class:
class output:

    def __init__(self, name: str, width: int, default: int) -> None:
        self.name    = name    # output signal name
        self.width   = width   # output signal width in bits
        self.default = default # output register default value

# Condition class:
class condition:

    def __init__(self, val1: type[input], val2: type[input]|int, comp_type: str) -> None:
        self.val1      = val1                   # input class instance
        self.val2      = val2                   # input class instance or integer
        self.comp_type = comp_type              # type of comparison
        
    def get_verilog(self) -> str:
        if isinstance(self.val2, int):          # val2 is an integer
            if self.val1.width == 1:            # Short version of condition is possible
                if self.val2 == 1 :             
                    code = self.val1.name
                else:
                    code = '!' + self.val1.name
            else:
                code = self.val1.name + ' ' + self.comp_type + ' ' + bin(self.val2)
        else:
            code = self.val1.name + ' ' + self.comp_type + ' ' + self.val2.name
        return code
        
    def get_graph(self):
        if isinstance(self.val2, int):          # val2 is an integer
            if self.val1.width == 1:            # Short version of condition is possible
                if self.val2 == 1 :             
                    label = self.val1.name
                else:
                    label = '!' + self.val1.name
            else:
                label = self.val1.name + ' ' + self.comp_type + ' ' + str(self.val2)
        else:
            label = self.val1.name + ' ' + self.comp_type + ' ' + self.val2.name 
        return label

# Output statement class:
class out_statement:

    def __init__(self, output: type[output], val: type[input]|int) -> None:
        self.output = output # output to assert
        self.val    = val    # value of output
    
    def get_graph(self):
        if isinstance(self.val, int):
            label = self.output.name + ' = ' + str(self.val)
        else:
            label = self.output.name + ' = ' + self.val.name
        return label

    def get_verilog(self):
        if isinstance(self.val, int):  
            return self.output.name + ' = ' + str(self.output.width) + '\'' + bin(self.val)[1:]
        else:
            return self.output.name + ' = ' + self.val.name
               
# State class:        
class state:

    def __init__(self, name: str, reset: bool) -> None:
        self.name  = name  # state name
        self.reset = reset # TRUE / FALSE: enter state @ reset
    
    def get_verilog(self):
        return self.name + ';'
    
    def get_graph(self):
        return self.name

# Edge class:
class edge:

    def __init__(self, source: type[state], dest: type[state], conditions: List[type[condition]], relations: List[str], out_statements: List[type[out_statement]]) -> None:
        self.source         = source         # state class to transition from
        self.dest           = dest           # state class to transition to
        self.conditions     = conditions     # List of input class instances
        self.relations      = relations      # List of (N-1) condition relations where N is len(conditions)
        self.out_statements = out_statements # List of output class instances
    
    def get_graph(self) -> str:
        label = ''
        for i in range(len(self.conditions)-1):
            label += self.conditions[i].get_graph() + ' ' + self.relations[i]
        label += self.conditions[-1].get_graph() + '\n('
        for i in range(len(self.out_statements)):
            label += self.out_statements[i].get_graph() + ' '
        return label + ')'
    
    def get_verilog_ns(self) -> str:
        condition_code = '('
        for i in range(len(self.conditions)-1):
            condition_code += self.conditions[i].get_verilog() + ' ' + self.relations[i]
        condition_code += self.conditions[-1].get_verilog() + ')'
        return condition_code
    
    def get_verilog_out(self) -> str:
        output_code = ''
        for i in range(len(self.out_statements)):
            output_code += self.out_statements[i].get_verilog()
        return output_code

# FSM class:      
class fsm:

    def __init__(self, inputs: List[input], outputs: List[output], edges: List[edge], states: List[state],  type='Mealy') -> None:
        self.graph   = graphviz.Digraph('FSM', filename='fsm.gv') # Create an empty directed graphviz graph
        self.inputs  = inputs                                     # List of input class instances
        self.outputs = outputs                                    # List of output class instances
        self.states  = states                                     # List of state class instances
        self.edges   = edges                                      # List of edge class instances
        self.type    = type                                       # Provision, in case moore machines are implemented, default is mealy
        self.clock   = input('clk', 1, 'clock')                   # Default clock
        self.reset   = input('rst_n', 1, 'reset')                 # Default reset
        self.default_state = state('IDLE', True)                  # Default IDLE state
        for i in range(len(self.inputs)):
            if self.inputs[i].type=='clock':                      
                self.clock = self.inputs[i]                       # Found clock in inputs, override default
            elif self.inputs[i].type=='reset':
                self.reset = self.inputs[i]                       # Found reset in inputs, override default
        for i in range(len(self.states)):
            if self.states[i].reset:
                self.default_state = self.states[i]               # Found default state in states, override default
        
    
    # This functions builds self.graph using self.statets_list and self.edges_dict
    def build_graph(self, path) -> None:
        
        # Add nodes:
        for state in self.states:
            self.graph.node(state.name)
        
        # Add edges:
        for edge in self.edges:
            self.graph.edge(edge.source.name, edge.dest.name, edge.get_graph())

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
            if self.inputs[i].type != 'clock' and self.inputs[i].type != 'reset':
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
            e_list = []
            for e in self.edges: 
                if e.source.name == s.name:
                    e_list.append(e)
            if len(e_list)==0:
                continue
            else:
                ns_logic += '      ' + s.name + ': begin\n'
                ns_logic += '         if ' + e_list[0].get_verilog_ns() + '\n'
                ns_logic += '            next_state = ' + e_list[0].dest.name + ';\n'
                for i in range(len(e_list)):
                    if i != 0:
                        ns_logic += '         else if ' + e_list[i].get_verilog_ns() + '\n'
                        ns_logic += '            next_state = ' + e_list[i].dest.name + ';\n'
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
            for e in self.edges: 
                if e.source.name == s.name:
                    out_logic += '         if (next_state == ' + e.dest.name + ')\n'
                    out_logic += '            ' + e.get_verilog_out() + ';\n'
            out_logic += '      ' + 'end\n'
        out_logic += '   endcase\n'
        out_logic += 'end\n'
        
        return out_logic + '\n'
        
    def get_verilog_footer(self) -> str:
        footer  = 'endmodule:ctrl\n\n'
        footer += '//| Enjoy! Esty                                  |//\n'
        return footer
