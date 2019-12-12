from .postprocessor_base import Postprocessor
from .postprocess_changelog import PostprocessChangelog

import dhtmlparser


class PostprocessIndex(Postprocessor):
    index_id = "702b4a57-5ecf-4c22-98f7-6a2786c46053"
    index_dom = None
    index_set = False
    index_already_processed = False

    @classmethod
    def postprocess(cls, dom, page, shared):
        if cls.index_already_processed:
            return

        if cls.index_set and PostprocessChangelog.is_set:
            content_el = cls.index_dom.find("div", {"id": "20c0a2f2-1f89-41fb-8a1d-b42e89b2ecb0"})[0]
            content_el.replaceWith(dhtmlparser.parseString(content_el.__str__() +
                                                           PostprocessChangelog.get_last_five_as_html_for_mainpage()))
            cls.index_already_processed = True
            return

        if cls.index_id not in page.content:
            return

        article = dom.find("article")
        if article and article[0].params.get("id") == cls.index_id:
            cls.index_dom = dom
            cls.index_set = True
