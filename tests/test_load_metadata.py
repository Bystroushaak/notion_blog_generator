import os.path

from pytest import fixture

from lib.virtual_fs import HtmlPage
from lib.preprocessors import LoadMetadata


@fixture(scope="module")
def page():
    fn = os.path.join(os.path.dirname(__file__), "critique_stub.html")
    with open(fn) as f:
        page = HtmlPage(f.read(), "critique_stub.html")

    LoadMetadata.parse_metadata_in_page(page)

    return page


def test_metadata_parser_image_index(page):
    assert page.metadata.image_index == 1


def test_metadata_parser_page_description(page):
    assert (
        page.metadata.page_description
        == """Patterns and structures of current operating systems and some thoughts about how that could be improved, with lessons learnt from Self, Smalltalk and other "structured" systems."""
    )


def test_metadata_parser_tags(page):
    assert page.metadata.tags == [
        "self",
        "python",
        "smalltalk",
        "programming_languages",
        "quest_for_structure",
        "os",
    ]


def test_metadata_unroll(page):
    assert page.metadata.unroll == True
