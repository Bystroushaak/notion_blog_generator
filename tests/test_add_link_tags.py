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

