from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .transformer_base import TransformerBase


class FixToggleBlocks(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Collapsing <details open> in toggle blocks..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        for ul_tag in page.dom.find("ul", {"class": "toggle"}):
            for details_tag in ul_tag.find("details"):
                details_tag.parameters.pop("open", None)
