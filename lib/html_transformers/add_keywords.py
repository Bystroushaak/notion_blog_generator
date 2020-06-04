import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddKeywordMetadataTags(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding <meta> keyword tag to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not page.metadata.tags:
            return

        meta_tag_str = '<meta name="keywords" content="%s">'
        meta_tag_str = meta_tag_str % ", ".join(page.metadata.tags)
        meta_tag = dhtmlparser.parseString(meta_tag_str).find("meta")[0]

        head = page.dom.find("head")[0]
        head.childs.append(meta_tag)
