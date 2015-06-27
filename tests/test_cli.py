import bootstrap  # noqa
import pytest

from modviz.cli import parse_arguments, validate_path, validate_fold_paths


def test_argument_parsing():
    with pytest.raises(SystemExit):
        parse_arguments([])

    namespace = parse_arguments(["foo"])
    assert namespace.path == "foo"
    assert namespace.target is None
    assert namespace.fold_paths is None
    assert namespace.exclude_paths is None

    namespace = parse_arguments(["foo", "-o", "test.html"])
    assert namespace.path == "foo"
    assert namespace.target is "test.html"
    assert namespace.fold_paths is None
    assert namespace.exclude_paths is None

    namespace = parse_arguments(["foo", "-o", "test.html", "-e", "foo", "bar"])
    assert namespace.path == "foo"
    assert namespace.target is "test.html"
    assert namespace.fold_paths is None
    assert namespace.exclude_paths == ["foo", "bar"]

    namespace = parse_arguments(["foo", "-o", "test.html", "-f", "foo", "bar"])
    assert namespace.path == "foo"
    assert namespace.target is "test.html"
    assert namespace.fold_paths == ["foo", "bar"]
    assert namespace.exclude_paths is None


def test_validate_path():
    assert validate_path("/")
    assert not validate_path("/imprettysureidontexist")


def test_validate_fold_paths():
    root = "/"
    assert validate_fold_paths(root, [])
    assert validate_fold_paths(root, ["/a", "/b"])

    with pytest.raises(ValueError):
        validate_fold_paths(root, ["foo"])
