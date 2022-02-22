import dhtmlparser3

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddAtomFeedTags(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Atom feed tag to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        head = page.dom.find("head")[0]

        atom_tag = dhtmlparser3.Tag(
            "link",
            parameters={
                "rel": "alternate",
                "type": "application/atom+xml",
                "href": page.root_section.changelog.atom_feed_url,
            },
            is_non_pair=True,
        )

        head[-1:] = atom_tag
