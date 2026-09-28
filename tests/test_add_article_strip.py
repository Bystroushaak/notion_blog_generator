from notion_blog_generator import glyphs
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import Directory
from notion_blog_generator.virtual_fs import RootSection
from notion_blog_generator.html_transformers.add_article_strip import AddArticleStrip

ARTICLE = """<html><head></head><body><article id="edb7f886-2aa3-4676-98a9-fcb9bd63c0b8" class="page sans">
<header><div class="page-header-icon undefined"><span class="icon" data-emoji="📂"></span></div>
<h1 class="page-title">Title</h1></header><div class="page-body"><p>text</p></div></article></body></html>"""


def built_page(html=ARTICLE):
    root = Directory("/")
    section = RootSection("en")
    root.add_subdir(section)
    section.set_parent(root)
    page = HtmlPage(html, "Title edb7f886-2aa3-4676-98a9-fcb9bd63c0b8.html")
    section.add_file(page)
    AddArticleStrip.transform(None, root, page)
    return page


def test_strip_replaces_notion_header_icon():
    page = built_page()
    header = page.dom.find("header")[0]
    assert header.find("div", fn=lambda x: "article-strip" in x.parameters.get("class", ""))
    assert not header.find("div", fn=lambda x: "page-header-icon" in x.parameters.get("class", ""))
    assert "data-emoji" not in str(header)


def test_explicit_added_to_article():
    page = built_page()
    assert page.dom.find("div", fn=lambda x: "explicit" in x.parameters.get("class", ""))


def test_article_strip_is_rust():
    assert glyphs.DYES["rust"][0] in str(built_page().dom)


def test_tag_page_gets_green_strip_and_no_explicit():
    page = built_page(ARTICLE.replace('class="page sans"', 'class="page sans tag-page"'))
    html = str(page.dom)
    assert "article-strip" in html
    assert glyphs.DYES["green"][0] in html
    assert 'class="explicit"' not in html
