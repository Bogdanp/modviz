import ast
import json
import os

from collections import namedtuple
from string import Template


def rel(*xs):
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), *xs)


with open(rel("static", "template.html")) as f:
    TEMPLATE = Template(f.read())


class ReferenceFinder(ast.NodeVisitor):
    def __init__(self, known_modules, module):
        self.known_modules = known_modules
        self.module = module
        self.references = set()

    def add(self, module):
        if module in self.known_modules:
            self.references.add(module)

    def visit_Import(self, node):
        for alias in node.names:
            self.add(self.module.absolute_ref(alias.name))

    def visit_ImportFrom(self, node):
        depth = node.level
        if depth == 0:
            module = self.module.absolute_ref(node.module)

            self.add(module)
        else:
            module = self.module.up_by(depth)
            if node.module is not None:
                module = module.relative_ref(node.module)
                self.add(module)

        for alias in node.names:
            self.add(module.relative_ref(alias.name))


class Module(namedtuple("Module", ("root", "filename",))):
    @staticmethod
    def filename_to_modulename(filename):
        modulename = filename.replace("/", ".")
        if modulename.endswith(".py"):
            return modulename[:-3]

        return "{}.__init__".format(modulename)

    @staticmethod
    def modulename_to_filename(modulename):
        return modulename.replace(".", "/") + ".py"

    @property
    def qualified_name(self):
        return self.filename_to_modulename(self.filename)

    @property
    def filepath(self):
        return os.path.join(self.root, self.filename)

    def absolute_ref(self, qualified_name):
        filename = self.modulename_to_filename(qualified_name)
        module = self.copy(filename=filename)
        return module

    def relative_ref(self, qualified_name):
        selfname = self.qualified_name.replace(".__init__", "")
        modulename = "{}.{}".format(selfname, qualified_name)
        filename = self.modulename_to_filename(modulename)
        module = self.copy(filename=filename)
        return module

    def up_by(self, n):
        filename = self.filename
        for i in range(n):
            filename = os.path.dirname(filename)

        return self.copy(filename=filename)

    def copy(self, root=None, filename=None):
        return Module(
            root=root or self.root,
            filename=filename or self.filename
        )

    def get_references(self, known_modules):
        with open(self.filepath) as f:
            contents = f.read()

        tree = ast.parse(contents)
        finder = ReferenceFinder(known_modules, self)
        finder.visit(tree)
        return finder.references

    def __str__(self):
        if self.qualified_name.endswith(".__init__"):
            return self.qualified_name.replace(".__init__", "")
        return self.qualified_name

    def __eq__(self, other):
        return self.qualified_name == other.qualified_name


def iterpackages(path):
    for root, dirs, _ in os.walk(path):
        for dirname in dirs:
            filepath = os.path.join(root, dirname)
            if os.path.exists(os.path.join(filepath, "__init__.py")):
                yield filepath


def itermodules(path):
    skipcount = len(path) + 1
    for package in iterpackages(path):
        for filename in os.listdir(package):
            filepath = os.path.join(package, filename)
            if filepath.endswith(".py") and os.path.isfile(filepath):
                yield Module(path, filepath[skipcount:])


def viz(path):
    nodes, edges = [], []
    modules = list(itermodules(path))
    for module in modules:
        nodes.append({
            "id": modules.index(module),
            "group": str(module).split(".")[0],
            "label": str(module)
        })

        for reference in module.get_references(modules):
            edges.append({
                "from": modules.index(module),
                "to": modules.index(reference)
            })

    return TEMPLATE.substitute(
        nodes=json.dumps(nodes, indent=4),
        edges=json.dumps(edges, indent=4)
    )
