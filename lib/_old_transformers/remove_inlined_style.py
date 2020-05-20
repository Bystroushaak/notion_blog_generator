import dhtmlparser

from .postprocessor_base import Postprocessor


class RemoveInlinedStyle(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        style = dom.match("head", "style")[0]

        style_path = shared.add_css(style.getContent())
        style_path = ("../" * (page.path.count("/") - 1)) + style_path

        style_str = '<link rel="stylesheet" type="text/css" href="%s">' % style_path
        new_style = dhtmlparser.parseString(style_str).find("link")[0]

        style.replaceWith(new_style)
