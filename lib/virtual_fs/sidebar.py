from typing import Tuple
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from lib.virtual_fs import HtmlPage
    from lib.virtual_fs import Directory

import dhtmlparser3
from dhtmlparser3 import Tag

from lib.settings import settings


class Sidebar:
    def __init__(self):
        self.ad_code = None
        self.last_five_html = None
        self.backlinks_html = None
        self.tagbox_html = None
        self.sections_html = None

    def add_to_page(self, page: 'HtmlPage') -> None:
        top_div, bottom_div = self._add_sidebar_skeletons_to_page(page)

        # twitter / rss buttons
        top_div[-1:] = self._get_feed_icons(page.root_section)
        bottom_div[-1:] = self._get_feed_icons(page.root_section)

        # last five
        last_five_top, last_five_bottom = self._get_last_five_tags()
        top_div[-1:] = last_five_top
        bottom_div[-1:] = last_five_bottom

        # backlinks
        if self.backlinks_html:
            backlinks_top, backlinks_bottom = self._get_backlinks_tags()
            top_div[-1:] = backlinks_top
            bottom_div[-1:] = backlinks_bottom

        # tagbox
        if self.tagbox_html:
            top_div[-1:] = self._get_tagbox_tag()
            bottom_div[-1:] = self._get_tagbox_tag()

        # sections
        top_div[-1:] = self._get_sections_tag()
        bottom_div[-1:] = self._get_sections_tag()

        # ads
        if self.ad_code:
            top_div[-1:] = self._get_advertisement_code_tag()

    def _add_sidebar_skeletons_to_page(self, page: 'HtmlPage') -> Tuple[Tag, Tag]:
        top_tag_code = """<div id="sidebar_top"></div>"""
        bottom_tag_code = '<div id="sidebar_bottom">\n</div>'

        top_tag = dhtmlparser3.parse(top_tag_code).find("div")[0]
        bottom_tag = dhtmlparser3.parse(bottom_tag_code).find("div")[0]

        body_tag = page.dom.find("body")[0]
        body_tag[0:] = top_tag
        body_tag[-1:] = bottom_tag

        return top_tag, bottom_tag

    def _get_last_five_tags(self) -> Tuple[Tag, Tag]:
        top_tag_code = f'<div id="last_five_top">\n{self.last_five_html}\n</div>'
        top_tag = dhtmlparser3.parse(top_tag_code).find("div")[0]

        bottom_tag_code = f'<div id="last_five_bottom">\n{self.last_five_html}\n</div>'
        bottom_tag = dhtmlparser3.parse(bottom_tag_code).find("div")[0]

        return top_tag, bottom_tag

    def _get_advertisement_code_tag(self) -> Tag:
        return dhtmlparser3.parse(self.ad_code)

    def _get_backlinks_tags(self) -> Tuple[Tag, Tag]:
        top_tag = dhtmlparser3.parse(self.backlinks_html).find("div")[0]
        bottom_tag = dhtmlparser3.parse(self.backlinks_html).find("div")[0]

        return top_tag, bottom_tag

    def _get_tagbox_tag(self) -> Tag:
        return dhtmlparser3.parse(self.tagbox_html).find("div")[0]

    def _get_sections_tag(self) -> Tag:
        return dhtmlparser3.parse(self.sections_html).find("div")[0]

    def _get_feed_icons(self, root) -> Tag:
        from lib.preprocessors.add_static_files import AddStaticFiles

        div_html = f"""
        <span>
            <a href="{root.root_section.changelog.atom_feed_url}"><img src="{AddStaticFiles.rss_icon_ref}" style="width: 3em;" /></a>
            &nbsp; &nbsp;
            <a href="{settings.twitter_url}"><img src="{AddStaticFiles.twitter_icon_ref}" style="width: 3em;" /></a>
        </span>
        """

        return dhtmlparser3.parse(div_html).find("span")[0]
