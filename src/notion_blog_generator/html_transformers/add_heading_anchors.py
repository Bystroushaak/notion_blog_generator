import uuid

import dhtmlparser3

from notion_blog_generator import glyphs

from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .transformer_base import TransformerBase
from .shorten_heading_ids import ShortenHeadingIds


class AddHeadingAnchors(TransformerBase):
    requires = [ShortenHeadingIds]

    HEADING_TAGS = frozenset(("h1", "h2", "h3", "h4", "h5", "h6"))

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding anchor links to headings..")

    @classmethod
    def _should_skip(cls, root: Directory, page: HtmlPage):
        if root is not None:
            if page is root.inner_index or page is root.outer_index:
                return True
        if page.is_category:
            return True
        if "/Changelog" in page.path:
            return True
        articles = page.dom.find("article")
        if articles:
            article_classes = articles[0].parameters.get("class", "").split()
            if "tag-page" in article_classes:
                return True
        return False

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if cls._should_skip(root, page):
            return

        for heading in page.dom.find("", fn=lambda x: x.name in cls.HEADING_TAGS):
            heading_id = heading.parameters.get("id", "")
            if not heading_id:
                continue
            classes = heading.parameters.get("class", "")
            if "page-title" in classes.split():
                continue
            anchor_html = (' <a class="heading-anchor" href="#%s"'
                           ' aria-label="Link to this heading">%s</a>'
                           % (heading_id, cls._heading_glyph(page, heading_id)))
            heading[-1:] = dhtmlparser3.parse(anchor_html)

    @staticmethod
    def _heading_glyph(page: HtmlPage, heading_id: str) -> str:
        """Every section of every page gets its own stable mark."""
        heading_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, f"{page.hash}#{heading_id}"))
        return glyphs.render_svg(glyphs.name_glyph(heading_uuid), glyphs.RUST)
