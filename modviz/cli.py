import argparse
import os
import sys

from . import viz


def parse_arguments(args=None):
    parser = argparse.ArgumentParser(description="Modviz lets you visualize your module dependencies.")
    parser.add_argument("path", metavar="PATH", help="the path to the package you want to visualize")
    parser.add_argument("-o", dest="target", help="the output file (default: stdout)")
    parser.add_argument("-f", dest="fold_paths", nargs="*", help="paths that need to be folded up ('vendor' dirs, for example)")
    parser.add_argument("-e", dest="exclude_paths", nargs="*", help="paths that should be excluded from the output")
    parser.add_argument("-x", dest="show_external", action="store_true", help="show external modules")
    parser.set_defaults(show_external=False)
    if args is None:  # pragma: no coverage
        return parser.parse_args()
    return parser.parse_args(args)


def validate_path(path):
    return os.path.exists(path) and os.path.isdir(path)


def validate_fold_paths(root, fold_paths):
    for fold_path in fold_paths:
        if not fold_path.startswith(root):
            raise ValueError(fold_path)

    return True


def main():  # pragma: no coverage
    arguments = parse_arguments()
    if not validate_path(arguments.path):
        sys.stderr.write("error: invalid PATH\n")
        return 1

    try:
        fold_paths = arguments.fold_paths or []
        validate_fold_paths(arguments.path, fold_paths)
    except ValueError as e:
        sys.stderr.write("error: invalid fold path '{}'\n".format(e.message))
        return 1

    result = viz(arguments.path, arguments.fold_paths, arguments.exclude_paths,
                 show_external=arguments.show_external)
    if arguments.target:
        with open(arguments.target, "w") as f:
            f.write(result)
    else:
        sys.stdout.write(result)

    return 0
