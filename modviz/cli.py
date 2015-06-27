import argparse
import os
import sys

from .modviz import viz


def parse_arguments():
    parser = argparse.ArgumentParser(description="Modviz lets you visualize your module dependencies.")
    parser.add_argument("path", metavar="PATH", help="the path to the package you want to visualize")
    parser.add_argument("-o", dest="target", help="the output file (default: stdout)")
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    if not os.path.exists(arguments.path) or \
       not os.path.isdir(arguments.path):
        sys.stderr.write("error: invalid PATH\n")
        return 1

    result = viz(arguments.path)
    if arguments.target:
        with open(arguments.target, "w") as f:
            f.write(result)
    else:
        sys.stdout.write(result)

    return 0
