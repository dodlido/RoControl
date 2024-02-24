##################################################################
#############         base_classes.py                 ############
# 1. input - input signal class, (name, width) ###################
# 2. output - output signal class, (name, width, default) ########
# 3. state - state class, (name, reset) ##########################
# 4. arch - ctrlr archs, (source, dest, cond, out, index) ########
##################################################################

# imports:
from boolean_parser import parse

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
        self.index = 0
        self.cond = parse(cond_str)
        self.out = parse(out_str)