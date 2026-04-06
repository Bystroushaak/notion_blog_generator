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
        # New Notion export: dirs with short disambiguation hash
        (
            "Environment and the programming language Self (par edb7-c0b8",
            "Environment and the programming language Self (par",
        ),
        # Short hash should NOT be stripped when in middle of path
        (
            "some dir abcd-ef01/image.png",
            "some dir abcd-ef01/image.png",
        ),
        # Dir without UUID stays the same
        (
            "Weekly update 2019 09 01; What I am working on",
            "Weekly update 2019 09 01; What I am working on",
        ),
    )

    for fucked, unfucked in filenames:
        assert UnfuckFilenames._unfuck_filename(fucked) == unfucked


def test_dir_matches_html_when_dir_has_no_uuid():
    """Dir: 'foo', HTML: 'foo abc123...def456.html' — should match."""
    root = Directory("/")

    subdir = Directory("Weekly update 2019 09 01")
    root.add_subdir(subdir)
    subdir.parent = root

    html = HtmlPage(
        "<body><h1 class='page-title'>Weekly update 2019/09/01; What I am working on</h1></body>",
        "Weekly update 2019 09 01 9c3129837e3a4e19a07f7bf6131f7cc5.html",
    )
    root.add_file(html)
    html.parent = root

    match = UnfuckFilenames._dir_in_parent_with_same_name_as(html)
    assert match is subdir


def test_dir_matches_html_when_dir_has_short_hash():
    """Dir: 'foo edb7-c0b8', HTML: 'foo edb7f886...c0b8.html' — should match."""
    root = Directory("/")

    subdir = Directory("Environment and Self (par edb7-c0b8")
    root.add_subdir(subdir)
    subdir.parent = root

    html = HtmlPage(
        "<body><h1 class='page-title'>Environment and Self (part two; language)</h1></body>",
        "Environment and Self (par edb7f8862aa3467698a9fcb9bd63c0b8.html",
    )
    root.add_file(html)
    html.parent = root

    match = UnfuckFilenames._dir_in_parent_with_same_name_as(html)
    assert match is subdir


def test_dir_matches_html_exact_match_still_works():
    """Old format: both have same UUID — exact match should still work."""
    root = Directory("/")

    subdir = Directory("Changelog 9439524048de45169fd74f5e92fb9598")
    root.add_subdir(subdir)
    subdir.parent = root

    html = HtmlPage(
        "<body><h1 class='page-title'>Changelog</h1></body>",
        "Changelog 9439524048de45169fd74f5e92fb9598.html",
    )
    root.add_file(html)
    html.parent = root

    match = UnfuckFilenames._dir_in_parent_with_same_name_as(html)
    assert match is subdir


def test_dir_matches_html_no_match_returns_none():
    root = Directory("/")

    subdir = Directory("Completely different name")
    root.add_subdir(subdir)
    subdir.parent = root

    html = HtmlPage(
        "<body><h1 class='page-title'>Some page</h1></body>",
        "Some page abc123def456abc123def456abc123de.html",
    )
    root.add_file(html)
    html.parent = root

    match = UnfuckFilenames._dir_in_parent_with_same_name_as(html)
    assert match is None


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


def test_only_alnum_chars_strips_apostrophes():
    assert UnfuckFilenames._only_alnum_chars("Godel's Proof") == "Godels Proof"


def test_only_alnum_chars_strips_parentheses():
    assert UnfuckFilenames._only_alnum_chars("Umira abicko (ano a drsne)") == "Umira abicko ano a drsne"


def test_only_alnum_chars_strips_semicolons():
    assert UnfuckFilenames._only_alnum_chars("Koronavirus; co bude dal") == "Koronavirus co bude dal"


def test_only_alnum_chars_strips_commas():
    assert UnfuckFilenames._only_alnum_chars("Zivy, syn Bdiciho") == "Zivy syn Bdiciho"


def test_only_alnum_chars_converts_slash_to_dash():
    assert UnfuckFilenames._only_alnum_chars("Control panels / alt interface") == "Control panels - alt interface"


def test_only_alnum_chars_preserves_dashes():
    assert UnfuckFilenames._only_alnum_chars("foo - bar") == "foo - bar"


def test_only_alnum_chars_preserves_underscores():
    assert UnfuckFilenames._only_alnum_chars("foo_bar") == "foo_bar"


def test_only_alnum_chars_preserves_plain_alnum():
    assert UnfuckFilenames._only_alnum_chars("Changelog") == "Changelog"


def test_remove_dup_underscores_collapses():
    assert UnfuckFilenames._remove_dup_underscores("foo__bar") == "foo_bar"


def test_remove_dup_underscores_strips_leading_trailing():
    assert UnfuckFilenames._remove_dup_underscores("_foo_") == "foo"


def test_remove_dup_underscores_no_op_on_clean():
    assert UnfuckFilenames._remove_dup_underscores("foo_bar") == "foo_bar"


def _normalize_dir(raw_name):
    """Mimic the directory normalization pipeline from UnfuckFilenames.preprocess."""
    name = UnfuckFilenames._unfuck_filename(raw_name)
    name = UnfuckFilenames.normalize(name)
    name = UnfuckFilenames._only_alnum_chars(name)
    name = UnfuckFilenames._remove_dup_underscores(name)
    return name


def test_dir_normalization_apostrophe():
    assert _normalize_dir("Godel's Proof abc123def456abc123def456abc123de") == "Godels Proof"


def test_dir_normalization_parentheses():
    assert _normalize_dir("Umira abicko (ano a drsne) abc123def456abc123def456abc123de") == "Umira abicko ano a drsne"


def test_dir_normalization_semicolon():
    assert _normalize_dir("Koronavirus; co bude dal abc123def456abc123def456abc123de") == "Koronavirus co bude dal"


def test_dir_normalization_comma():
    assert _normalize_dir("Zivy, syn Bdiciho abc123def456abc123def456abc123de") == "Zivy syn Bdiciho"


def test_dir_normalization_diacritics_stripped():
    assert _normalize_dir("Změny abc123def456abc123def456abc123de") == "Zmeny"


def test_dir_normalization_clean_unchanged():
    assert _normalize_dir("Changelog abc123def456abc123def456abc123de") == "Changelog"


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
