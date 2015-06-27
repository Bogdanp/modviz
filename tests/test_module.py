import bootstrap  # noqa
import pytest
import os

from modviz import Module


def test_filename_conversion():
    assert Module.filename_to_modulename("foo/bar/baz.py") == "foo.bar.baz"
    assert Module.filename_to_modulename("foo/bar") == "foo.bar.__init__"
    assert Module.filename_to_modulename("foo.py") == "foo"
    assert Module.filename_to_modulename("foo") == "foo.__init__"

    with pytest.raises(AssertionError):
        assert Module.filename_to_modulename("")


def test_modulename_conversion():
    assert Module.modulename_to_filename("foo.bar.baz") == "foo/bar/baz.py"
    assert Module.modulename_to_filename("foo.bar") == "foo/bar.py"
    assert Module.modulename_to_filename("foo") == "foo.py"

    with pytest.raises(AssertionError):
        assert Module.modulename_to_filename("")


def test_standard_qualified_names():
    module = Module("/", "foo/bar.py")
    assert module.qualified_name == "foo.bar"

    module = Module("/", "foo/bar")
    assert module.qualified_name == "foo.bar.__init__"


def test_virtual_qualified_names():
    module = Module("/", "foo/bar.py", "bar.py")
    assert module.qualified_name == "bar"

    module = Module("/", "foo/bar", "bar")
    assert module.qualified_name == "bar.__init__"


def test_module_defaults():
    module = Module("/", "foo.py")
    assert module.virtual_filename is None
    assert module.virtual_diff is None

    module = Module("/", "foo.py", "bar.py")
    assert module.virtual_filename == "bar.py"


def test_filepath():
    root, filename = "/", "foo.py"
    assert Module(root, filename).filepath == os.path.join(root, filename)


def test_folding():
    module = Module("/foo/bar", "baz/boo.py")
    module = module.fold("/foo/bar/baz")
    assert module.filepath == "/foo/bar/baz/boo.py"
    assert module.filename == "baz/boo.py"
    assert module.virtual_filename == "boo.py"
    assert module.virtual_diff == "baz"

    with pytest.raises(AssertionError):
        Module("/foo/bar", "baz/boo.py").fold("baz")


def test_absolute_ref():
    module = Module("/", "foo.py").absolute_ref("os.path")
    assert module.root == "/"
    assert module.filepath == "/os/path.py"
    assert module.filename == "os/path.py"
    assert module.virtual_filename is None
    assert module.virtual_diff is None

    module = Module("/", "foo.py", "bar.py").absolute_ref("os.path")
    assert module.root == "/"
    assert module.filepath == "/os/path.py"
    assert module.filename == "os/path.py"
    assert module.virtual_filename is None
    assert module.virtual_diff is None


def test_relative_ref():
    module = Module("/", "foo.py").relative_ref("os.path")
    assert module.root == "/"
    assert module.qualified_name == "foo.os.path"
    assert module.filepath == "/foo/os/path.py"
    assert module.filename == "foo/os/path.py"
    assert module.virtual_filename is None
    assert module.virtual_diff is None

    module = Module("/", "foo/bar.py").relative_ref("os.path")
    assert module.root == "/"
    assert module.qualified_name == "foo.bar.os.path"
    assert module.filepath == "/foo/bar/os/path.py"
    assert module.filename == "foo/bar/os/path.py"
    assert module.virtual_filename is None
    assert module.virtual_diff is None

    module = Module("/", "foo/bar").relative_ref("os.path")
    assert module.root == "/"
    assert module.qualified_name == "foo.bar.os.path"
    assert module.filepath == "/foo/bar/os/path.py"
    assert module.filename == "foo/bar/os/path.py"
    assert module.virtual_filename is None
    assert module.virtual_diff is None

    module = Module("/libs", "foo/bar.py")
    module = module.fold("/libs/foo")
    module = module.relative_ref("os.path")
    assert module.root == "/libs"
    assert module.qualified_name == "bar.os.path"
    assert module.filepath == "/libs/foo/bar/os/path.py"
    assert module.filename == "foo/bar/os/path.py"
    assert module.virtual_filename == "bar/os/path.py"
    assert module.virtual_diff == "foo"


def test_up_by():
    module = Module("/", "foo/bar/baz.py")
    assert module.up_by(1).qualified_name == "foo.bar.__init__"
    assert module.up_by(2).qualified_name == "foo.__init__"

    module = Module("/foo", "sub/bar/baz.py")
    module = module.fold("/foo/sub")
    module = module.up_by(1)
    assert module.qualified_name == "bar.__init__"
    assert module.filepath == "/foo/sub/bar"
    assert module.filename == "sub/bar"
    assert module.virtual_filename == "bar"
