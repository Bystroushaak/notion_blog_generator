from urllib.parse import quote

import dhtmlparser3

from notion_blog_generator import glyphs
from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddFaviconLinkTags(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding favicon <link> tag to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        head = page.dom.find("head")[0]

        if glyphs.is_page_uuid(page.pretty_hash):
            svg = glyphs.render_svg(glyphs.name_glyph(page.pretty_hash), glyphs.RUST)
            head[-1:] = dhtmlparser3.Tag(
                "link",
                parameters={
                    "rel": "icon",
                    "type": "image/svg+xml",
                    "href": "data:image/svg+xml," + quote(svg),
                },
                is_non_pair=True,
            )

        favicon_tag = dhtmlparser3.Tag(
            "link",
            parameters={"rel": "shortcut icon", "href": "/favicon.ico"},
            is_non_pair=True,
        )
        head[-1:] = favicon_tag
