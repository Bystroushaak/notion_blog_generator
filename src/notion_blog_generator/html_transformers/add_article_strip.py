import dhtmlparser3

from notion_blog_generator import glyphs
from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddArticleStrip(TransformerBase):
    """
    Hang the page's glyph strip next to the title and close articles with the
    name glyph, like the explicit mark at the end of a manuscript text.
    """

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding glyph strips to pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if cls._should_skip(root, page):
            return

        header = page.dom.find("header")[0]

        # the strip is the page's identity now, Notion's emoji icon would compete with it
        for icon in header.find(
            "div", fn=lambda x: "page-header-icon" in x.parameters.get("class", "")
        ):
            icon.parent.remove_item(icon)

        strip = glyphs.render_strip(
            page.pretty_hash, page.glyph_language, page.glyph_dye, page.pictogram
        )
        strip_html = f'<div class="article-strip" aria-hidden="true">{strip}</div>'
        header[0:] = dhtmlparser3.parse(strip_html)

        if page.is_category or page.is_tag_page or page.pictogram:
            return

        explicit = glyphs.render_svg(glyphs.name_glyph(page.pretty_hash), glyphs.RUST)
        explicit_html = f'<div class="explicit" aria-hidden="true">{explicit}</div>'
        page.dom.find("article")[0][-1:] = dhtmlparser3.parse(explicit_html)

    @classmethod
    def _should_skip(cls, root: Directory, page: HtmlPage) -> bool:
        if page is root.inner_index or page is root.outer_index:
            return True

        if not glyphs.is_page_uuid(page.pretty_hash):
            return True

        return not page.dom.find("article") or not page.dom.find("header")
