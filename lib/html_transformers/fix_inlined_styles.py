import dhtmlparser

from lib.settings import settings

from .transformer_base import TransformerBase


class FixInlinedStyles(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Postprocessing inlined <style> tags..")

    @classmethod
    def transform(cls, virtual_fs, root, page):
        for item in page.dom.find("", fn=lambda x: "style" in x.params):
            if item.getTagName() == "figure":
                cls._postprocess_figure(item)

    @classmethod
    def _postprocess_figure(cls, item):
        new_style = item.params["style"].replace("white-space:pre-wrap;", "")
        item.params["style"] = new_style
