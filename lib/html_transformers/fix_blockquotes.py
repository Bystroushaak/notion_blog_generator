import dhtmlparser3

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
        for blockquote_tag in page.dom.find("blockquote"):
            content = blockquote_tag.content_str(escape=True)
            if "\n" not in content:
                continue

            alt_content = content.replace("\n", "<br />\n")
            blockquote_tag.content = dhtmlparser3.parse(alt_content).content
