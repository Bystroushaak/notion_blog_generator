from dhtmlparser3 import Tag

from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .transformer_base import TransformerBase
from .add_heading_anchors import AddHeadingAnchors


class AddIncipit(TransformerBase):
    """
    Mark the first real paragraph of an article, so the CSS can turn its first
    letter into a manuscript-style initial.
    """

    MIN_LENGTH = 120
    NOT_BODY_TEXT = frozenset(("table", "figure", "blockquote", "li", "details", "summary"))

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Marking article incipits..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if AddHeadingAnchors._should_skip(root, page):
            return

        for paragraph in page.dom.find("p"):
            if cls._is_opening_paragraph(paragraph):
                classes = paragraph.parameters.get("class", "").split()
                paragraph.parameters["class"] = " ".join(classes + ["incipit"])
                return

    @classmethod
    def _is_opening_paragraph(cls, paragraph: Tag) -> bool:
        if len(paragraph.content_without_tags().strip()) < cls.MIN_LENGTH:
            return False

        in_page_body = False
        parent = paragraph.parent
        while parent is not None:
            if parent.name in cls.NOT_BODY_TEXT:
                return False

            classes = parent.parameters.get("class", "").split()
            if "column" in classes:
                return False
            if "page-body" in classes:
                in_page_body = True

            parent = parent.parent

        return in_page_body
