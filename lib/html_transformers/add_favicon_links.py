import dhtmlparser3

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddFaviconLinkTags(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding favicon <link> tag to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        favicon_tag = dhtmlparser3.Tag(
            "link",
            parameters={"rel": "shortcut icon", "href": "/favicon.ico"},
            is_non_pair=True,
        )
        page.dom.find("head")[0][-1:] = favicon_tag
