import argparse
import sys
from examples.examples import cntr_exmp, cmp_exmp

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
    out_folder, graph, verilog = flag_parser()
    # Get FSM:
    counter = cntr_exmp()
    if (graph):
        # Generate graph:
        counter.build_graph(out_folder)
    if (verilog):
        # Generate verilog:
        counter.build_verilog(out_folder)

if __name__ == "__main__":
    main()