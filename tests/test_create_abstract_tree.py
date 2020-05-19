#! /usr/bin/env python3
import os.path

from pytest import fixture

from lib.preprocessors.create_abstract_tree import ResourceRegistry
from lib.preprocessors.create_abstract_tree import VirtualFS
from lib.preprocessors.create_abstract_tree import _patch_filename

from lib.preprocessors.create_abstract_tree import Data
from lib.preprocessors.create_abstract_tree import HtmlPage
from lib.preprocessors.create_abstract_tree import Directory


@fixture()
def tree():
    root = Directory("/")

    subdir = Directory("subdir")
    root.add_subdir(subdir)
    subdir.parent = root

    file_in_root = HtmlPage("<body><img src='subdir/img.jpg' /></body>",
                            "file_in_root.html")
    root.add_file(file_in_root)
    file_in_root.parent = root

    file_in_subdir = HtmlPage("<body><a href='../file_in_root.html'>asd</a></body>",
                              'file_in_subdir.html')
    subdir.add_file(file_in_subdir)
    file_in_subdir.parent = subdir

    image_in_subdir = Data('/subdir/img.jpg', 'IMG_CONTENT')
    subdir.add_file(image_in_subdir)
    image_in_subdir.parent = subdir

    return root


def test_patch_filename():
    filenames = (
        ("Bystroushaak s blog 702b4a575ecf4c2298f76a2786c46053.html",
         "Bystroushaak s blog.html"),
        ("Paperclips tr ky acd2a190121b46c4a5351f39a00e5cf1.html",
         "Paperclips tr ky.html"),
        ("Control panels alt interface 260648f08d0e4e7ea82d973a72a550e0",
         "Control panels alt interface"),
        ("Active%20widget%20in%20PyQT5%20QTextEdit%20a35a5d6bff794aa8b78d198babf0bbbc/example_window.png",
         "Active%20widget%20in%20PyQT5%20QTextEdit/example_window.png")
    )

    for fucked, unfucked in filenames:
        assert _patch_filename(fucked) == unfucked


def test_path_property(tree):
    subdir = tree.subdirs[0]
    file_in_subdir = subdir.files[0]

    assert subdir.path == "/subdir"
    assert file_in_subdir.path == "/subdir/file_in_subdir.html"


def test_resource_registry(tree):
    rr = ResourceRegistry(tree)

    root_id = rr.add_item("/")
    subdir_id = rr.add_item("/subdir")

    assert root_id is not None
    assert subdir_id is not None

    assert rr.item_by_id(root_id)
    assert rr.item_by_id(subdir_id)

    assert rr.item_by_path("/")
    assert rr.item_by_path("/subdir")

    assert rr.path_by_id(root_id) == "/"
    assert rr.path_by_id(subdir_id) == "/subdir"

    assert rr.id_by_path("/") == root_id
    assert rr.id_by_path("/subdir") == subdir_id


def test_create_abstract_tree():
    dirname = os.path.dirname(__file__)
    zipfile = os.path.join(dirname, "structure.zip")

    virtual_fs = VirtualFS(zipfile)

    assert virtual_fs

    index_id = virtual_fs.resource_registry.id_by_path("/index.html")
    assert index_id > 0

    index = virtual_fs.resource_registry.item_by_id(index_id)
    assert "resource:4" in index.dom.__str__()
