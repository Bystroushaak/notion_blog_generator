import dhtmlparser

from lib.settings import settings

from .transformer_base import TransformerBase


class AddAtomFeed(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding atom feed to all pages..")

    @classmethod
    def transform(cls, virtual_fs, root, page):
        head = page.dom.find("head")[0]

        atom_tag_str = (
            '<link rel="alternate" type="application/atom+xml" '
            'href="http://rfox.eu/raw/feeds/notion_blog.xml" />'
        )
        atom_tag = dhtmlparser.parseString(atom_tag_str).find("link")[0]

        head.childs.append(atom_tag)
