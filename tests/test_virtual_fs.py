#! /usr/bin/env python3
import os
import zipfile

import pytest

from notion_blog_generator.virtual_fs import _unwrap_nested_zip
from notion_blog_generator.virtual_fs import iterate_zipfile


def _make_flat_zip(path, entries):
    with zipfile.ZipFile(path, "w") as zf:
        for name, data in entries.items():
            zf.writestr(name, data)


def _make_nested_zip(path, inner_path, inner_entries):
    _make_flat_zip(inner_path, inner_entries)
    with zipfile.ZipFile(path, "w") as zf:
        zf.write(inner_path, arcname=os.path.basename(inner_path))


def test_unwrap_flat_zip_returns_original(tmp_path):
    flat = tmp_path / "flat.zip"
    _make_flat_zip(flat, {"a.txt": "AAA", "b.txt": "BBB"})

    actual, is_temp = _unwrap_nested_zip(str(flat))

    assert actual == str(flat)
    assert is_temp is False


def test_unwrap_nested_zip_extracts_to_temp(tmp_path):
    nested = tmp_path / "nested.zip"
    inner = tmp_path / "inner.zip"
    _make_nested_zip(nested, inner, {"x.txt": "XXX", "y.txt": "YYY"})

    actual, is_temp = _unwrap_nested_zip(str(nested))

    assert is_temp is True
    assert actual != str(nested)
    assert os.path.exists(actual)
    with zipfile.ZipFile(actual) as zf:
        assert sorted(zf.namelist()) == ["x.txt", "y.txt"]
        assert zf.read("x.txt") == b"XXX"

    os.unlink(actual)


def test_iterate_zipfile_cleans_up_temp_on_success(tmp_path, monkeypatch):
    nested = tmp_path / "nested.zip"
    inner = tmp_path / "inner.zip"
    _make_nested_zip(nested, inner, {"x.txt": "XXX", "y.txt": "YYY"})

    deleted = []
    original_unlink = os.unlink
    monkeypatch.setattr(os, "unlink", lambda p: (deleted.append(p), original_unlink(p)))

    names = [info.filename for _, info in iterate_zipfile(str(nested))]

    assert sorted(names) == ["x.txt", "y.txt"]
    assert len(deleted) == 1
    assert not os.path.exists(deleted[0])


def test_iterate_zipfile_cleans_up_temp_on_exception(tmp_path, monkeypatch):
    nested = tmp_path / "nested.zip"
    inner = tmp_path / "inner.zip"
    _make_nested_zip(nested, inner, {"x.txt": "XXX", "y.txt": "YYY"})

    deleted = []
    original_unlink = os.unlink
    monkeypatch.setattr(os, "unlink", lambda p: (deleted.append(p), original_unlink(p)))

    with pytest.raises(RuntimeError):
        for _, info in iterate_zipfile(str(nested)):
            raise RuntimeError("boom")

    assert len(deleted) == 1
    assert not os.path.exists(deleted[0])
