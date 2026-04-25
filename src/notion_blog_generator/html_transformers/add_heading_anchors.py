import dhtmlparser3

from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .transformer_base import TransformerBase
from .shorten_heading_ids import ShortenHeadingIds


class AddHeadingAnchors(TransformerBase):
    requires = [ShortenHeadingIds]

    HEADING_TAGS = frozenset(("h1", "h2", "h3", "h4", "h5", "h6"))
    ANCHOR_SYMBOL = "🔗"

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
                           % (heading_id, cls.ANCHOR_SYMBOL))
            heading[-1:] = dhtmlparser3.parse(anchor_html)
