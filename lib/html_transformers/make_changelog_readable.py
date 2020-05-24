from collections import namedtuple

import dhtmlparser

from lib.settings import settings

from .transformer_base import TransformerBase


class Post(namedtuple("Post", "timestamp, title, description")):
    pass


class MakeChangelogReadable(TransformerBase):
    last_articles = []
    is_set = False
    changelog_id = "94395240-48de-4516-9fd7-4f5e92fb9598"

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Converting Changelog table to readable page..")

    @classmethod
    def transform(cls, virtual_fs, root, page):
        article_tag = page.dom.find("article")
        if not article_tag or article_tag[0].params.get("id") != cls.changelog_id:
            return

        content_element = "<div>\n"
        tr_line_template = "  <p><span class=\"changelog_short\">%s</span> (%s)</p>\n%s"
        tr_line_template += "  <hr style=\"margin-bottom: 1em; margin-top: 1em;\"/>\n\n"

        tbody = article_tag[0].find("tbody")[0]
        for tr in reversed(tbody.find("tr")):
            td_date, td_title, td_content = tr.find("td")

            content = cls._parse_content(td_content)
            post = Post(td_date.getContent(), td_title.getContent(), content)

            tr_line = tr_line_template % (post.title, post.timestamp, post.description)
            content_element += tr_line

            cls.last_articles.append(post)

        content_element += "</div>\n"

        cls.is_set = True

        table_content_el = dhtmlparser.parseString(content_element).find("div")[0]
        article_tag[0].find("table")[0].replaceWith(table_content_el)

    @classmethod
    def _parse_content(cls, td_content):
        content = td_content.find("a")
        if content and content[0].getContent() == "Untitled":
            content = ""
        elif not content:
            raise ValueError("Changelog doesn't contain link. Please add it.")
        else:
            content_template = "<p class=\"changelog_description\"><em>%s</em></p>\n"
            content = content_template % content[0].getContent()

        return content

    @classmethod
    def get_articles_as_html_for_root_index(cls, how_many=5):
        output = "<h1>Recent posts</h1>\n<div class=\"recent_posts\">\n"
        template = "  <h4 class=\"changelog_short\">%s (%s)</h4>\n<p>%s</p>"

        updates = []
        for cnt, post in enumerate(cls.last_articles):
            if cnt >= how_many:
                break

            updates.append(template % (post.title, post.timestamp, post.description))

        output += "\n".join(updates)

        output += "</div>\n"

        return output

    @classmethod
    def get_last_five_for_sidebars(cls):
        output = "<h3>New posts:</h3>\n<ul>\n"

        for post in cls.last_articles:
            output += "  <li>%s</li>\n" % post.title

        output += "</ul>\n"
        output += "\n& <a href=\"/Changelog.html\">more</a>"

        return output
