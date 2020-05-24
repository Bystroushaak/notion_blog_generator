import dhtmlparser

from lib.settings import settings

from .transformer_base import TransformerBase


class AddAtomFeedTag(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Atom feed tag to all pages..")

    @classmethod
    def transform(cls, virtual_fs, root, page):
        head = page.dom.find("head")[0]

        atom_tag_str = (
            '<link rel="alternate" type="application/atom+xml" '
            'href="%s" />'
        )
        atom_tag_str = atom_tag_str % settings.atom_feed_url
        atom_tag = dhtmlparser.parseString(atom_tag_str).find("link")[0]

        head.childs.append(atom_tag)
