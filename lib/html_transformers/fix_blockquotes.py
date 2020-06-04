import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class FixBlockquotes(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Fixing newlines in <blockquote> tags..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        # keep newlines in <blockquote> tags
        for p in page.dom.find("blockquote"):
            for text in p.find(None, fn=lambda x: not x.isTag()):
                if "\n" not in text.getContent():
                    continue

                alt_content = text.getContent().replace("\n", "<br />")
                text.replaceWith(dhtmlparser.parseString(alt_content))
