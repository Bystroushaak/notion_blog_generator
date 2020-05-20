import dhtmlparser

from .postprocessor_base import Postprocessor


class AddPatreonButton(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        html_code = (
            '<div class="corner-ribbon top-right red">'
            '<a href="https://www.patreon.com/bePatron?u=2618881">Become a Patron</a>'
            '</div>'
        )
        button_tag = dhtmlparser.parseString(html_code)

        dom.find("body")[0].childs.append(button_tag)
