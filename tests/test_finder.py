import ast
import bootstrap  # noqa

from modviz import Module
from modviz.modviz import ReferenceFinder


def test_find_simple_from():
    modules = [Module("/", "foo/bar.py"), Module("/", "baz/__init__.py")]
    source = "from baz import Baz"
    finder = ReferenceFinder(modules, modules[0])
    finder.visit(ast.parse(source))
    assert finder.references == set([Module("/", "baz.py")])


def test_package_relative_from():
    modules = [Module("/", "foo/bar.py"), Module("/", "foo/baz.py")]
    source = "from . import bar"
    finder = ReferenceFinder(modules, modules[1])
    finder.visit(ast.parse(source))
    assert finder.references == set([Module("/", "foo/bar.py")])

def test_find_external():
    modules = [Module("/", "foo/bar.py")]
    source = "import baz"
    finder = ReferenceFinder(modules, modules[0])
    finder.visit(ast.parse(source))
    assert finder.ext_references == set([Module("/", "baz.py")])

def test_find_external_dot():
    modules = [Module("/", "foo/bar.py")]
    source = "import baz.bazz"
    finder = ReferenceFinder(modules, modules[0])
    finder.visit(ast.parse(source))
    assert finder.ext_references == set([Module("/", "baz/bazz.py")])

def test_find_external_from_import():
    modules = [Module("/", "foo/bar.py")]
    source = "from baz import bazz"
    finder = ReferenceFinder(modules, modules[0])
    finder.visit(ast.parse(source))
    assert finder.ext_references == set([
        Module("/", "baz.py"),
        Module("/", "baz/bazz.py")
    ])
