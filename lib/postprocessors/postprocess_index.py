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
            content_el = cls.index_dom.find("h1", {"id": "93217684-c41c-49f8-88b4-347410b2c330"})[0]
            changelog = PostprocessChangelog.get_last_five_as_html_for_mainpage()
            content_el.replaceWith(dhtmlparser.parseString(changelog + content_el.__str__()))
            cls.index_already_processed = True
            return

        if cls.index_id not in page.content:
            return

        article = dom.find("article")
        if article and article[0].params.get("id") == cls.index_id:
            cls.index_dom = dom
            cls.index_set = True

            cls._insert_twitter_and_rss_buttons(dom)

    @classmethod
    def _insert_twitter_and_rss_buttons(cls, dom):
        feed_mention_paragraph = dom.find("p", {"id": "bd75b1ce-a053-435a-bad4-df9a25c87e6f"})[0]

        div_html = """
        <div align="center">
            <a href="http://kitakitsune.org/raw/feeds/notion_blog.xml">
                <img src="icons/rss_icon.png" style="width: 4em;" />
            </a>
            &nbsp; &nbsp;
            <a href="https://twitter.com/bystroushaak">
                <img src="icons/twitter_icon.png" style="width: 4em;" />
            </a>
        </div>
        """
        feed_mention_paragraph.childs.append(dhtmlparser.parseString(div_html))
