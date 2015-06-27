import ast
import bootstrap  # noqa

from modviz import Module
from modviz.modviz import ReferenceFinder


def test_find_simple_from():
    modules = [Module("/", "foo/bar.py"), Module("/", "baz")]
    source = "from baz import Baz"
    finder = ReferenceFinder(modules, modules[0])
    finder.visit(ast.parse(source))
    assert finder.references == set([Module("/", "baz.py")])


def test_package_relative_from():
    modules = [Module("/", "foo"), Module("/", "foo/bar.py"), Module("/", "baz")]
    source = "from . import Baz"
    finder = ReferenceFinder(modules, modules[0])
    finder.visit(ast.parse(source))
    assert finder.references == set([Module("/", "foo")])
