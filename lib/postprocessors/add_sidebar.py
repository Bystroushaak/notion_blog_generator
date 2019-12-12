import dhtmlparser

from .postprocessor_base import Postprocessor
from .postprocess_changelog import PostprocessChangelog


class AddSidebar(Postprocessor):
    all_pages = []

    @classmethod
    def postprocess(cls, dom, page, shared):
        cls.all_pages.append((dom, page))

    @classmethod
    def add_to_all_relevant_pages(cls):
        print("Adding sidebars..")

        sidebar_content = PostprocessChangelog.get_last_five_for_sidebars()

        top_tag_code = '<div id="sidebar_top">\n%s\n</div>' % sidebar_content
        bottom_tag_code = '<div id="sidebar_bottom">\n%s\n</div>' % sidebar_content
        top_tag = dhtmlparser.parseString(top_tag_code).find("div")[0]
        bottom_tag = dhtmlparser.parseString(bottom_tag_code).find("div")[0]

        for dom, page in cls.all_pages:
            if page.is_index:
                continue

            body_tag = dom.find("body")[0]
            body_tag.childs.insert(0, top_tag)
            body_tag.childs.append(bottom_tag)
