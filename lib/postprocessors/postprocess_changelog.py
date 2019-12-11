from .postprocessor_base import Postprocessor

import dhtmlparser


class PostprocessChangelog(Postprocessor):
    last_five = "<h2>New posts</h2>\n<div>\n"
    is_set = False

    @classmethod
    def postprocess(cls, dom, page, shared):
        article = dom.find("article")
        if not article or article[0].params.get("id") != "94395240-48de-4516-9fd7-4f5e92fb9598":
            return

        content_element = "<div>\n"
        tr_line_template = "  <p>%s <span class=\"changelog_short\">%s</span></p>\n%s"
        tr_line_template += "  <hr style=\"margin-bottom: 1em; margin-top: 1em;\"/>\n\n"

        tbody = article[0].find("tbody")[0]
        for cnt, tr in enumerate(reversed(tbody.find("tr"))):
            td_content, td_date, td_title = tr.find("td")

            content = td_content.find("a")
            if content and content[0].getContent() == "Untitled":
                content = ""
            else:
                content = "<p class=\"changelog_description\"><em>%s</em></p>\n" % content[0].getContent()

            tr_line = tr_line_template % (td_date.getContent(), td_title.getContent(), content)
            content_element += tr_line

            if cnt < 5:
                cls.last_five += tr_line

        content_element += "</div>\n"
        cls.last_five += "</div>\n"
        cls.is_set = True

        table_content_el = dhtmlparser.parseString(content_element).find("div")[0]
        article[0].find("table")[0].replaceWith(table_content_el)
