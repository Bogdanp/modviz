import argparse
import os
import sys

from .modviz import viz


def parse_arguments():
    parser = argparse.ArgumentParser(description="Modviz lets you visualize your module dependencies.")
    parser.add_argument("path", metavar="PATH", help="the path to the package you want to visualize")
    parser.add_argument("-o", dest="target", help="the output file (default: stdout)")
    parser.add_argument("-f", dest="fold_paths", nargs="*", help="paths that need to be folded up ('vendor' dirs, for example)")
    parser.add_argument("-e", dest="exclude_paths", nargs="*", help="paths that should be excluded from the output")
    return parser.parse_args()


def main():
    arguments = parse_arguments()
    if not os.path.exists(arguments.path) or \
       not os.path.isdir(arguments.path):
        sys.stderr.write("error: invalid PATH\n")
        return 1

    fold_paths = arguments.fold_paths or []
    for fold_path in fold_paths:
        if not fold_path.startswith(arguments.path):
            sys.stderr.write("error: invalid fold path '{}'\n".format(fold_path))
            return 1

    result = viz(arguments.path, arguments.fold_paths, arguments.exclude_paths)
    if arguments.target:
        with open(arguments.target, "w") as f:
            f.write(result)
    else:
        sys.stdout.write(result)

    return 0
