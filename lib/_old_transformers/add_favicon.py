import dhtmlparser

from .postprocessor_base import Postprocessor


class AddFavicon(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        favicon_code = '<link rel="shortcut icon" href="http://blog.rfox.eu/favicon.ico">'
        favicon_tag = dhtmlparser.parseString(favicon_code)
        dom.find("head")[0].childs.append(favicon_tag)