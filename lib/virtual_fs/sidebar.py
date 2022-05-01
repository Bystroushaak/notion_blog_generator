import copy
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
        self.changelog_ref = None

    def add_to_page(self, page: "HtmlPage") -> None:
        top_div, bottom_div = self._add_sidebar_skeletons_to_page(page)

        # twitter / rss buttons for top on top
        top_div[-1:] = self._get_feed_icons(page.root_section)

        # last five
        last_five_top, last_five_bottom = self._get_last_five_tags()
        top_div[-1:] = Tag("h3", content=["New posts"])
        top_div.content.extend(last_five_top)
        top_div.content.extend(
            [
                "\n& ",
                Tag("a", parameters={"href": self.changelog_ref}, content=["more"]),
            ]
        )

        bottom_div[-1:] = Tag("hr", is_non_pair=True)
        bottom_div[-1:] = Tag(
            "p",
            content=[
                "Did you enjoy the blogpost? Here are other posts from this blog:"
            ],
        )
        bottom_div.content.extend(last_five_bottom)
        bottom_div[-1:] = Tag(
            "p",
            content=[
                "You can find ",
                Tag(
                    "a",
                    parameters={"href": self.changelog_ref},
                    content=["many more in changelog"],
                ),
                "..",
            ],
        )

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

        # twitter / rss buttons for bottom
        bottom_div[-1:] = Tag("h3", content="Follow this blog")
        bottom_div[-1:] = self._get_feed_icons(page.root_section, big=True)

        # ads
        if self.ad_code:
            top_div[-1:] = self._get_advertisement_code_tag()

    def _add_sidebar_skeletons_to_page(self, page: "HtmlPage") -> Tuple[Tag, Tag]:
        top_tag = Tag("div", parameters={"id": "sidebar_top"})
        bottom_tag = Tag("div", parameters={"id": "sidebar_bottom"})

        body_tag = page.dom.find("body")[0]
        body_tag[0:] = top_tag
        body_tag[-1:] = bottom_tag

        return top_tag, bottom_tag

    def _get_last_five_tags(self) -> Tuple[Tag, Tag]:
        top_tag = Tag("div", parameters={"id": "last_five_top"})
        bottom_tag = Tag("div", parameters={"id": "last_five_bottom"})

        ul = Tag("ul")
        for post in self.last_five_html:
            link_tag = Tag("a", parameters={"href": post.link}, content=[post.title])
            ul[-1:] = Tag("li", content=[link_tag])

        top_tag[-1:] = ul
        bottom_tag[-1:] = copy.deepcopy(ul)

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

    def _get_feed_icons(self, root, big=False) -> Tag:
        from lib.preprocessors.add_static_files import AddStaticFiles

        style = "width: 3em;"
        if big:
            style = "width: 5em;"

        div = Tag("div")
        div.content = [
            Tag("p"),
            self._img_in_link(
                root.root_section.changelog.atom_feed_url,
                AddStaticFiles.rss_icon_ref,
                style,
            ),
            "\u00A0\u00A0\u00A0 \u00A0\u00A0\u00A0",  # nbsp
            self._img_in_link(
                settings.twitter_url, AddStaticFiles.twitter_icon_ref, style
            ),
            "\u00A0\u00A0\u00A0 \u00A0\u00A0\u00A0",  # nbsp
            self._img_in_link(
                settings.patreon_url, AddStaticFiles.patreon_icon_ref, style
            ),
        ]

        return div

    def _img_in_link(self, link: str, img_ref: str, img_style: str) -> Tag:
        img_tag = Tag(
            "img",
            parameters={"src": img_ref, "style": img_style},
            is_non_pair=True,
        )

        return self._tag_in_link(link, img_tag)

    def _tag_in_link(self, link: str, tag: Tag) -> Tag:
        return Tag("a", parameters={"href": link}, content=[tag])
