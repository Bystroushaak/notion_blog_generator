import dhtmlparser3
from pytest import mark

from notion_blog_generator.postprocessors.add_link_tags import AddLinkTags


def link(html):
    return dhtmlparser3.parse(html).find("a")[0]


@mark.parametrize(
    "html, expected",
    [
        ('<a href="x">📂 3D modeling</a>', "3D modeling"),
        ('<a href="x">📄 Some article</a>', "Some article"),
        ('<a href="x">  📂 Indented</a>', "Indented"),
        ('<a href="x">Plain title</a>', "Plain title"),
        ('<a href="x">A 📂 in the middle</a>', "A 📂 in the middle"),
    ],
)
def test_strip_icon(html, expected):
    tag = link(html)
    AddLinkTags._strip_icon(tag)
    assert tag.content_without_tags() == expected


def test_strip_icon_removes_icon_span():
    tag = link('<a href="x"><span class="icon">📄</span>Some article</a>')
    AddLinkTags._strip_icon(tag)
    assert tag.content_without_tags() == "Some article"
    assert not tag.find("span")


def test_strip_icon_leaves_tag_content_alone():
    tag = link('<a href="x"><img src="i.png"></a>')
    AddLinkTags._strip_icon(tag)
    assert tag.find("img")


@mark.parametrize(
    "html, expected",
    [
        ('<p>📚 <a href="x">Books</a> (since 2010)</p>', "<p><a"),
        ('<p>Read the 📚 <a href="x">Books</a></p>', "<p>Read the <a"),
        ('<p>Plain <a href="x">Books</a></p>', "<p>Plain <a"),
        ('<p><a href="x">Books</a></p>', "<p><a"),
    ],
)
def test_strip_preceding_icon(html, expected):
    dom = dhtmlparser3.parse(html)
    AddLinkTags._strip_preceding_icon(dom.find("a")[0])
    assert str(dom).startswith(expected)
