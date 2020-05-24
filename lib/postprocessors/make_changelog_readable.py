from collections import namedtuple

import dhtmlparser

from lib.settings import settings

from .postprocessor_base import PostprocessorBase


class Post(namedtuple("Post", "timestamp, title, description")):
    pass


class MakeChangelogReadable(PostprocessorBase):
    is_set = False
    last_articles = []

    @classmethod
    def postprocess(cls, virtual_fs, root):
        settings.logger.info("Converting Changelog table to readable page..")

        changelog_dir = root.subdir_by_name("Changelog")

        cls.make_changelog_readable(changelog_dir.inner_index)
        cls.make_changelog_readable(changelog_dir.outer_index)

        # remove "table" files
        changelog_dir.files = [file for file in changelog_dir.files
                               if file.is_index]

        cls.is_set = True

    @classmethod
    def make_changelog_readable(cls, changelog_page):
        content_element = "<div>\n"
        tr_line_template = "  <p><span class=\"changelog_short\">%s</span> (%s)</p>\n%s"
        tr_line_template += "  <hr style=\"margin-bottom: 1em; margin-top: 1em;\"/>\n\n"

        tbody = changelog_page.dom.find("tbody")[0]
        for tr in reversed(tbody.find("tr")):
            td_date, td_title, td_content = tr.find("td")

            content = cls._parse_content(td_content)
            post = Post(td_date.getContent(), td_title.getContent(), content)

            tr_line = tr_line_template % (post.title, post.timestamp, post.description)
            content_element += tr_line

            cls.last_articles.append(post)

        content_element += "</div>\n"

        table_content_el = dhtmlparser.parseString(content_element).find("div")[0]
        changelog_page.dom.find("table")[0].replaceWith(table_content_el)

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
