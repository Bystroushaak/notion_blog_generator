import dhtmlparser

from lib.settings import settings
from lib.preprocessors import AddStaticFiles

from .transformer_base import TransformerBase


class ReplaceInlinedStyles(TransformerBase):
    _initialized = False
    _inlined_style_str = ""

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Removing inlined styles..")

    @classmethod
    def transform(cls, virtual_fs, root, page):
        style = page.dom.match("head", "style")[0]

        cls._initialize(style.getContent())

        style_str = '<link rel="stylesheet" type="text/css" href="%s">'
        style_str = style_str % AddStaticFiles.css_ref

        new_style = dhtmlparser.parseString(style_str).find("link")[0]
        style.replaceWith(new_style)

    @classmethod
    def _initialize(cls, original_css):
        if cls._initialized:
            return

        original_css = original_css.replace("white-space: pre-wrap;\n", "", 1)
        cls._inlined_style_str = original_css

        css_as_bytes = bytes(original_css, "utf-8")
        AddStaticFiles.css.content = css_as_bytes + AddStaticFiles.css.content

        cls._initialized = True
