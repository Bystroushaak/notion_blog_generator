from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.html_transformers.add_incipit import AddIncipit

LONG = "I bring you a message about a language that has been at the birth of many others, but almost no one knows it. A rumor of a graphical environment."


def incipits(body):
    page = HtmlPage(
        f'<html><body><article><div class="page-body">{body}</div></article></body></html>',
        "t.html",
    )
    AddIncipit.transform(None, None, page)
    return [
        p.content_without_tags()
        for p in page.dom.find("p")
        if "incipit" in p.parameters.get("class", "")
    ]


def test_first_long_paragraph_is_marked():
    assert incipits(f"<p>Note:</p><p>{LONG}</p><p>{LONG} again</p>") == [LONG]


def test_short_paragraphs_are_skipped():
    assert incipits("<p>@2019/05/19</p><p>short</p>") == []


def test_paragraphs_in_tables_and_quotes_are_skipped():
    body = f"<table><tr><td><p>{LONG} table</p></td></tr></table><blockquote><p>{LONG} quote</p></blockquote><p>{LONG}</p>"
    assert incipits(body) == [LONG]


def test_paragraphs_in_columns_are_skipped():
    body = f'<div class="column-list"><div class="column"><p>{LONG} column</p></div></div><p>{LONG}</p>'
    assert incipits(body) == [LONG]


def test_existing_class_is_kept():
    page = HtmlPage(
        f'<html><body><div class="page-body"><p class="x">{LONG}</p></div></body></html>', "t.html"
    )
    AddIncipit.transform(None, None, page)
    assert page.dom.find("p")[0].parameters["class"] == "x incipit"
