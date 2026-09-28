from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.html_transformers.fix_inlined_styles import FixInlinedStyles


def styles_after_fix(html):
    page = HtmlPage(html, "t.html")
    FixInlinedStyles.transform(None, None, page)
    return [tag.parameters["style"] for tag in page.dom.find("", fn=lambda x: "style" in x.parameters)]


def test_pre_wrap_removed_from_figure():
    assert styles_after_fix('<figure style="white-space:pre-wrap;display:flex"></figure>') == ["display:flex"]


def test_pre_wrap_removed_from_aside_callout():
    html = '<aside class="callout" data-notion-callout="" style="white-space:pre-wrap;display:flex"></aside>'
    assert styles_after_fix(html) == ["display:flex"]


def test_other_elements_untouched():
    assert styles_after_fix('<code style="white-space:pre-wrap;word-break:break-all"></code>') == [
        "white-space:pre-wrap;word-break:break-all"
    ]
