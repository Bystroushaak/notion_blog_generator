import dhtmlparser

from .postprocessor_base import Postprocessor


class AddAtomFeed(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        head = dom.find("head")[0]

        atom_tag_str = (
            '<link rel="alternate" type="application/atom+xml" '
            'href="http://rfox.eu/raw/feeds/notion_blog.xml" />'
        )
        atom_tag = dhtmlparser.parseString(atom_tag_str).find("link")[0]

        head.childs.append(atom_tag)
