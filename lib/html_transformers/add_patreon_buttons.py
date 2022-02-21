import dhtmlparser3

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddPatreonButtons(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Patreon button to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not settings.patreon_url:
            return

        button_tag = dhtmlparser3.Tag(
            "div",
            parameters={"class": "corner-ribbon top-right red"},
        )
        link_tag = dhtmlparser3.Tag(
            "a", parameters={"href": settings.patreon_url}, content=["Become a Patron"]
        )
        button_tag[0:] = link_tag

        page.dom.find("body")[0][-1:] = button_tag
