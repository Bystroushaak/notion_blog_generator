import dhtmlparser

from lib.settings import settings

from .transformer_base import TransformerBase


class FixBlockquotes(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Fixing newlines in <blockquote> tags..")

    @classmethod
    def transform(cls, virtual_fs, root, page):
        # keep newlines in <blockquote> tags
        for p in page.dom.find("blockquote"):
            for text in p.find(None, fn=lambda x: not x.isTag()):
                if "\n" not in text.getContent():
                    continue

                alt_content = text.getContent().replace("\n", "<br />")
                text.replaceWith(dhtmlparser.parseString(alt_content))
