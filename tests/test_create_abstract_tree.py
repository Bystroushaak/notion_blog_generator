#! /usr/bin/env python3
import os.path

from pytest import fixture

from notion_blog_generator.virtual_fs import ResourceRegistry
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.preprocessors.unfuck_filenames import UnfuckFilenames
from notion_blog_generator.preprocessors.generate_indexes_for_directories import (
    _strip_diacritics,
    GenerateIndexesForDirectories,
)

from notion_blog_generator.virtual_fs import Data
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import Directory


@fixture()
def tree():
    root = Directory("/")

    subdir = Directory("subdir")
    root.add_subdir(subdir)
    subdir.parent = root

    file_in_root = HtmlPage(
        "<body><img src='subdir/img.jpg' /></body>", "file_in_root.html"
    )
    root.add_file(file_in_root)
    file_in_root.parent = root

    file_in_subdir = HtmlPage(
        "<body><a href='../file_in_root.html'>asd</a></body>", "file_in_subdir.html"
    )
    subdir.add_file(file_in_subdir)
    file_in_subdir.parent = subdir

    image_in_subdir = Data("/subdir/img.jpg", "IMG_CONTENT")
    subdir.add_file(image_in_subdir)
    image_in_subdir.parent = subdir

    return root


def test_patch_filename():
    filenames = (
        (
            "Bystroushaak s blog 702b4a575ecf4c2298f76a2786c46053.html",
            "Bystroushaak s blog.html",
        ),
        (
            "Paperclips tr ky acd2a190121b46c4a5351f39a00e5cf1.html",
            "Paperclips tr ky.html",
        ),
        (
            "Control panels alt interface 260648f08d0e4e7ea82d973a72a550e0",
            "Control panels alt interface",
        ),
        (
            "Active%20widget%20in%20PyQT5%20QTextEdit%20a35a5d6bff794aa8b78d198babf0bbbc/example_window.png",
            "Active%20widget%20in%20PyQT5%20QTextEdit/example_window.png",
        ),
    )

    for fucked, unfucked in filenames:
        assert UnfuckFilenames._unfuck_filename(fucked) == unfucked


def test_path_property(tree):
    subdir = tree.subdirs[0]
    file_in_subdir = subdir.files[0]

    assert subdir.path == "/subdir"
    assert file_in_subdir.path == "/subdir/file_in_subdir.html"


def test_resource_registry(tree):
    rr = ResourceRegistry()

    root_id = rr.register_item("/")
    subdir_id = rr.register_item("/subdir")

    assert root_id is not None
    assert subdir_id is not None

    assert rr.item_by_id(root_id)
    assert rr.item_by_id(subdir_id)

    assert rr.id_by_item("/") == root_id
    assert rr.id_by_item("/subdir") == subdir_id


def test_create_abstract_tree():
    dirname = os.path.dirname(__file__)
    zipfile = os.path.join(dirname, "structure.zip")

    virtual_fs = VirtualFS(zipfile)

    assert virtual_fs

    index = virtual_fs.root.files[0]
    index_id = virtual_fs.resource_registry.id_by_item(index)
    assert index_id >= 0

    index = virtual_fs.resource_registry.item_by_id(index_id)
    assert "resource:4" in index.dom.__str__()


def test_strip_diacritics_removes_czech_diacritics():
    assert _strip_diacritics("Změny") == "Zmeny"
    assert _strip_diacritics("Představení") == "Predstaveni"
    assert _strip_diacritics("příliš žluťoučký kůň") == "prilis zlutoucky kun"


def test_strip_diacritics_preserves_ascii():
    assert _strip_diacritics("Changelog") == "Changelog"
    assert _strip_diacritics("hello_world") == "hello_world"


def test_strip_diacritics_empty():
    assert _strip_diacritics("") == ""


def test_files_with_dirname_matches_with_diacritics_mismatch():
    """Regression test: Notion export may have dir 'Změny' but file 'Zmeny.html'."""
    root = Directory("/")

    subdir = Directory("Změny")
    root.add_subdir(subdir)
    subdir.parent = root

    html_file = HtmlPage("<body>changelog</body>", "Zmeny.html")
    root.add_file(html_file)
    html_file.parent = root

    matches = list(GenerateIndexesForDirectories._files_with_dirname(subdir, "Změny"))
    assert len(matches) == 1
    assert matches[0] == (subdir, html_file)


def test_files_with_dirname_exact_match_still_works():
    root = Directory("/")

    subdir = Directory("Changelog")
    root.add_subdir(subdir)
    subdir.parent = root

    html_file = HtmlPage("<body>changelog</body>", "Changelog.html")
    root.add_file(html_file)
    html_file.parent = root

    matches = list(GenerateIndexesForDirectories._files_with_dirname(subdir, "Changelog"))
    assert len(matches) == 1
    assert matches[0] == (subdir, html_file)


def test_convert_resources_to_paths_skips_missing_resource():
    """Regression test: missing resource should not crash, just skip."""
    root = Directory("/")

    page = HtmlPage(
        "<body><a href='resource:9999'>link</a></body>",
        "page.html",
    )
    root.add_file(page)
    page.parent = root

    rr = ResourceRegistry()
    # resource:9999 is NOT registered -> should skip gracefully
    page.convert_resources_to_paths(rr)

    # href should remain unchanged (not crash)
    a_tag = page.dom.find("a")[0]
    assert a_tag["href"] == "resource:9999"


def test_convert_resources_to_paths_resolves_valid_resource():
    root = Directory("/")

    target = HtmlPage("<body><h1 class='page-title'>target</h1></body>", "target.html")
    root.add_file(target)
    target.parent = root

    rr = ResourceRegistry()
    target_id = rr.register_item(target)
    ref_str = rr.as_ref_str(target_id)

    page = HtmlPage(
        f"<body><a href='{ref_str}'>link</a></body>",
        "page.html",
    )
    root.add_file(page)
    page.parent = root

    page.convert_resources_to_paths(rr)

    a_tag = page.dom.find("a")[0]
    assert a_tag["href"] == "target.html"
    assert a_tag["title"] == "target"
