import graphviz
from typing import List, Union

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
                    code = self.val1.name + ';'
                else:
                    code = '!' + self.val1.name + ';'
            else:
                code = self.val1.name + ' ' + self.comp_type + ' ' + bin(self.val2) + ';'
        else:
            code = self.val1.name + ' ' + self.comp_type + ' ' + self.val2.name + ';'
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
        return self.get_graph() + ';'
               
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
        self.relations      = relations      # List of condition relations
        self.out_statements = out_statements # List of output class instances
    
    def get_graph(self) -> str:
        label = ''
        for i in range(len(self.conditions)):
            label += self.conditions[i].get_graph() + ' ' + self.relations[i]
        label += '\n('
        for i in range(len(self.out_statements)):
            label += self.out_statements[i].get_graph() + ' '
        return label + ')'
    
    def get_verilog(self):
        condition_code, output_code = '(', ''
        for i in range(len(self.conditions)):
            condition_code += self.conditions[i].get_verilog() + ' ' + self.relations[i]
        condition_code += ')'
        for i in range(len(self.out_statements)):
            output_code += self.out_statements[i].get_verilog() + '\n'
        return condition_code, output_code

# FSM class:      
class fsm:

    def __init__(self, inputs: List[input], outputs: List[output], edges: List[edge], states: List[state],  type='Mealy') -> None:
        self.graph   = graphviz.Digraph('FSM', filename='fsm.gv') # Create an empty directed graphviz graph
        self.inputs  = inputs                                     # List of input class instances
        self.outputs = outputs                                    # List of output class instances
        self.states  = states                                     # List of state class instances
        self.edges   = edges                                      # List of edge class instances
        self.type    = type                                       # Provision, in case moore machines are implemented, default is mealy
    
    # This functions builds self.graph using self.statets_list and self.edges_dict
    def build_graph(self):
        
        # Add nodes:
        for state in self.states:
            self.graph.node(state.name)
        
        # Add edges:
        for edge in self.edges:
            self.graph.edge(edge.source.name, edge.dest.name, edge.get_graph())
        
        self.graph.render('test_output/fsm.gv').replace('\\', '/')

