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
        self.ext_references = set()

    def add(self, module):
        if module != self.module:
            if module in self.known_modules:
                self.references.add(module)
            else:
                self.ext_references.add(module)

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


class Module(namedtuple("Module", ("root", "filename", "virtual_filename", "virtual_diff"))):
    def __new__(cls, root, filename, virtual_filename=None, virtual_diff=None):
        return super(Module, cls).__new__(cls, root, filename, virtual_filename, virtual_diff)

    @staticmethod
    def filename_to_modulename(filename):
        assert filename, "empty filename"
        modulename = filename.replace("/", ".")
        if modulename.endswith(".py"):
            return modulename[:-3]

        return modulename

    @staticmethod
    def modulename_to_filename(modulename):
        assert modulename, "empty modulename"
        return modulename.replace(".", "/") + ".py"

    @property
    def qualified_name(self):
        if self.virtual_filename is None:
            name = self.filename_to_modulename(self.filename)
        else:
            name = self.filename_to_modulename(self.virtual_filename)

        return name.replace(".__init__", "")

    @property
    def filepath(self):
        return os.path.join(self.root, self.filename)

    def fold(self, path):
        assert path.startswith(self.root), "invalid fold path"
        path = path[len(self.root) + 1:]
        filename = self.filename[len(path) + 1:]
        return self.copy(virtual_filename=filename, virtual_diff=path)

    def absolute_ref(self, qualified_name):
        return Module(self.root, self.modulename_to_filename(qualified_name))

    def relative_ref(self, qualified_name):
        modulename = "{}.{}".format(self.qualified_name, qualified_name)
        filename = self.modulename_to_filename(modulename)
        if self.virtual_filename:
            virtual_filename = filename
            filename = os.path.join(self.virtual_diff, filename)
            return self.copy(filename=filename, virtual_filename=virtual_filename)
        return self.copy(filename=filename)

    def up_by(self, n):
        virtual_filename = self.virtual_filename
        filename = self.filename
        for i in range(n):
            filename = os.path.dirname(filename)
            if self.virtual_filename:
                virtual_filename = os.path.dirname(virtual_filename)

        return self.copy(
            filename=filename,
            virtual_filename=virtual_filename
        )

    def copy(self, root=None, filename=None, virtual_filename=None, virtual_diff=None):
        return Module(
            root=root or self.root,
            filename=filename or self.filename,
            virtual_filename=virtual_filename or self.virtual_filename,
            virtual_diff=virtual_diff or self.virtual_diff
        )

    def get_references(self, known_modules):
        with open(self.filepath) as f:
            contents = f.read()

        tree = ast.parse(contents)
        finder = ReferenceFinder(known_modules, self)
        finder.visit(tree)
        return finder.references, finder.ext_references

    def __str__(self):
        return self.qualified_name

    def __eq__(self, other):
        return self.qualified_name == other.qualified_name

    def __ne__(self, other):
        return self.qualified_name != other.qualified_name


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


def viz(path, fold_paths=None, exclude_paths=None, show_external=False):
    fold_paths = fold_paths or []
    exclude_paths = exclude_paths or []
    nodes, edges, modules, ext_modules, dataset = [], [], [], [], set()
    for module in itermodules(path):
        exclude = False

        for exclude_path in exclude_paths:
            if module.filepath.startswith(exclude_path):
                exclude = True
                break

        for fold_path in fold_paths:
            if module.filepath.startswith(fold_path):
                module = module.fold(fold_path)

        if not exclude:
            modules.append(module)

    for module in modules:
        idx = modules.index(module)
        if idx not in dataset:
            dataset.add(idx)
            nodes.append({
                "id": idx,
                "group": str(module).split(".")[0],
                "label": str(module)
            })

        references, ext_references = module.get_references(modules)

        for reference in references:
            edges.append({
                "from": modules.index(module),
                "to": modules.index(reference)
            })

        if show_external:
            for ext_reference in ext_references:
                if ext_reference not in ext_modules:
                    nodes.append({
                        "id": len(modules) + len(ext_modules),
                        "group": str(ext_reference).split(".")[0],
                        "label": str(ext_reference)
                    })
                    ext_modules.append(ext_reference)
                edges.append({
                    "from": modules.index(module),
                    "to": len(modules) + ext_modules.index(ext_reference)
                })

    return TEMPLATE.substitute(
        nodes=json.dumps(nodes, indent=4),
        edges=json.dumps(edges, indent=4)
    )
