from dhtmlparser3 import Tag

from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .transformer_base import TransformerBase


class FixInlinedStyles(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Postprocessing inlined <style> tags..")

    # callouts used to be <figure>, newer Notion exports make them <aside>
    PRE_WRAP_CONTAINERS = frozenset(("figure", "aside"))

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        containers = page.dom.find(
            "", fn=lambda x: x.name in cls.PRE_WRAP_CONTAINERS and "style" in x.parameters
        )
        for item in containers:
            cls._postprocess_figure(item)

    @classmethod
    def _postprocess_figure(cls, item: Tag):
        item["style"] = item["style"].replace("white-space:pre-wrap;", "")
