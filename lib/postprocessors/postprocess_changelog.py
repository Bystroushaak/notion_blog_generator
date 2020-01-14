from collections import namedtuple

from .postprocessor_base import Postprocessor

import dhtmlparser


class Post(namedtuple("Post", "timestamp, title, description")):
    pass


class PostprocessChangelog(Postprocessor):
    last_five = []
    is_set = False

    @classmethod
    def postprocess(cls, dom, page, shared):
        article = dom.find("article")
        if not article or article[0].params.get("id") != "94395240-48de-4516-9fd7-4f5e92fb9598":
            return

        content_element = "<div>\n"
        tr_line_template = "  <p><span class=\"changelog_short\">%s</span> (%s)</p>\n%s"
        tr_line_template += "  <hr style=\"margin-bottom: 1em; margin-top: 1em;\"/>\n\n"

        tbody = article[0].find("tbody")[0]
        for cnt, tr in enumerate(reversed(tbody.find("tr"))):
            td_content, td_date, td_title = tr.find("td")

            content = td_content.find("a")
            if content and content[0].getContent() == "Untitled":
                content = ""
            else:
                content = "<p class=\"changelog_description\"><em>%s</em></p>\n" % content[0].getContent()

            post = Post(td_date.getContent(), td_title.getContent(), content)

            tr_line = tr_line_template % (post.title, post.timestamp, post.description)
            content_element += tr_line

            if cnt < 5:
                cls.last_five.append(post)

        content_element += "</div>\n"

        cls.is_set = True

        table_content_el = dhtmlparser.parseString(content_element).find("div")[0]
        article[0].find("table")[0].replaceWith(table_content_el)

    @classmethod
    def get_last_five_as_html_for_mainpage(cls):
        output = "<h1>Recent posts</h1>\n<div class=\"recent_posts\">\n"
        template = "  <h4 class=\"changelog_short\">%s (%s)</h4>\n<p>%s</p>"

        updates = []
        for post in cls.last_five:
            updates.append(template % (post.title, post.timestamp, post.description))

        output += "\n".join(updates)

        output += "</div>\n"

        return output

    @classmethod
    def get_last_five_for_sidebars(cls):
        output = "<h3>New posts:</h3>\n<ul>\n"

        for post in cls.last_five:
            output += "  <li>%s</li>\n" % post.title

        output += "</ul>\n"
        output += "\n& <a href=\"/Changelog.html\">more</a>"

        return output
