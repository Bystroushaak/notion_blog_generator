from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .transformer_base import TransformerBase


class FixCodeBlocksDir(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Forcing dir=ltr on <pre class=code> blocks..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        for pre_tag in page.dom.find("pre"):
            classes = pre_tag.parameters.get("class", "")
            if "code" not in classes.split():
                continue
            pre_tag.parameters["dir"] = "ltr"
