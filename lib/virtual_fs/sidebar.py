from functools import lru_cache

from typing import Tuple
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.virtual_fs import HtmlPage
    from lib.virtual_fs import Directory

import dhtmlparser
from dhtmlparser import HTMLElement

from lib.settings import settings


class Sidebar:
    def __init__(self):
        self.ad_code = None
        self.last_five_html = None
        self.backlinks_html = None
        self.tagbox_html = None
        self.sections_html = None

    def add_to_page(self, page: 'HtmlPage', root: 'Directory') -> None:
        top_div, bottom_div = self._add_sidebar_skeletons_to_page(page)

        # twitter / rss buttons
        top_div.childs.append(self._get_feed_icons(root))
        bottom_div.childs.append(self._get_feed_icons(root))

        # last five
        last_five_top, last_five_bottom = self._get_last_five_tags()
        top_div.childs.append(last_five_top)
        bottom_div.childs.append(last_five_bottom)

        # backlinks
        if self.backlinks_html:
            backlinks_top, backlinks_bottom = self._get_backlinks_tags()
            top_div.childs.append(backlinks_top)
            bottom_div.childs.append(backlinks_bottom)

        # tagbox
        if self.tagbox_html:
            top_div.childs.append(self._get_tagbox_tag())

        # sections
        top_div.childs.append(self._get_sections_tag())

        # ads
        if self.ad_code:
            top_div.childs.append(self._get_advertisement_code_tag())

    def _add_sidebar_skeletons_to_page(self, page: 'HtmlPage') -> Tuple[HTMLElement, HTMLElement]:
        top_tag_code = """<div id="sidebar_top"></div>"""
        bottom_tag_code = '<div id="sidebar_bottom">\n</div>'

        top_tag = dhtmlparser.parseString(top_tag_code).find("div")[0]
        bottom_tag = dhtmlparser.parseString(bottom_tag_code).find("div")[0]

        body_tag = page.dom.find("body")[0]
        body_tag.childs.insert(0, top_tag)
        body_tag.childs.append(bottom_tag)

        return top_tag, bottom_tag

    def _get_last_five_tags(self):
        top_tag_code = '<div id="last_five_top">\n%s\n</div>' % self.last_five_html
        top_tag = dhtmlparser.parseString(top_tag_code).find("div")[0]

        bottom_tag_code = '<div id="last_five_bottom">\n%s\n</div>' % self.last_five_html
        bottom_tag = dhtmlparser.parseString(bottom_tag_code).find("div")[0]

        return top_tag, bottom_tag

    def _get_advertisement_code_tag(self):
        return dhtmlparser.parseString(self.ad_code)

    def _get_backlinks_tags(self):
        top_tag = dhtmlparser.parseString(self.backlinks_html).find("div")[0]
        bottom_tag = dhtmlparser.parseString(self.backlinks_html).find("div")[0]

        return top_tag, bottom_tag

    def _get_tagbox_tag(self):
        return dhtmlparser.parseString(self.tagbox_html).find("div")[0]

    def _get_sections_tag(self):
        return dhtmlparser.parseString(self.sections_html).find("div")[0]

    @lru_cache()
    def _get_feed_icons(self, root):
        from lib.preprocessors.add_static_files import AddStaticFiles

        div_html = """
        <span>
            <a href="{rss_feed_url}"><img src="{rss_icon_url}" style="width: 3em;" /></a>
            &nbsp; &nbsp;
            <a href="{twitter_url}"><img src="{twitter_icon_url}" style="width: 3em;" /></a>
        </span>
        """
        div_html = div_html.format(rss_feed_url=root.root_section.changelog.atom_feed_url,
                                   rss_icon_url=AddStaticFiles.rss_icon_ref,
                                   twitter_url=settings.twitter_url,
                                   twitter_icon_url=AddStaticFiles.twitter_icon_ref)

        return dhtmlparser.parseString(div_html).find("span")[0]
