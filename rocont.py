import argparse
import sys
from rocontrol.roclass import * 
from examples.counter import *

def flag_parser():
    # Instantiate the parser:
    parser = argparse.ArgumentParser(description='RoControl - FSM graphs and verilog generation')
    # Path to output folder:
    parser.add_argument('-o', '--out_folder', type=str, help='Path to desired output folder')
    # Create graph flag:
    parser.add_argument('-g', '--graph', action='store_true', help='I want a nice graph')
    # Create code flag:
    parser.add_argument('-v', '--verilog', action='store_true', help='I want a nice module')
    # Check if empty flags:
    if len(sys.argv)==1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    # Parse:
    args = parser.parse_args()
    return args.out_folder, args.graph, args.verilog

def main():
    debug = False
    if not debug:
        out_folder, graph, verilog = flag_parser()
    else:
        graph, debug, out_folder = True, True, 'out_debug'
    # Get FSM:
    fsm = get_fsm()
    if (graph):
        # Generate graph:
        fsm.build_graph(out_folder)
    if (verilog):
        # Generate verilog:
        fsm.build_verilog(out_folder)

if __name__ == "__main__":
    main()