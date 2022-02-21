from dhtmlparser3 import Tag

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class FixInlinedStyles(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Postprocessing inlined <style> tags..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        for item in page.dom.find("figure", fn=lambda x: "style" in x.parameters):
            cls._postprocess_figure(item)

    @classmethod
    def _postprocess_figure(cls, item: Tag):
        item["style"] = item["style"].replace("white-space:pre-wrap;", "")
