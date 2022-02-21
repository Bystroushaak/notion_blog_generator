from html import escape

import dhtmlparser3

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddMetaTags(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding <meta> tags to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not page.metadata:
            return

        head = page.dom.find("head")[0]

        if page.metadata.page_description:
            meta = cls._add_meta_tag("description", page.metadata.page_description)
            head[-1:] = meta

        if page.metadata.tags:
            tags = page.metadata.tags[:]
            tags.append("m0wFG3PRCoJVTs7JcgBwsOXb3U7yPxBB")
            meta = cls._add_meta_tag("keywords", ",".join(tags), escape_html=False)
            head[-1:] = meta

    @classmethod
    def _add_meta_tag(cls, name, content, escape_html=True) -> dhtmlparser3.Tag:
        content = content.replace('"', "&quote;")

        if escape_html:
            return dhtmlparser3.Tag(
                "meta",
                parameters={"name": escape(name), "content": content},
                is_non_pair=True,
            )

        return dhtmlparser3.Tag(
            "meta",
            parameters={"name": name, "content": content},
            is_non_pair=True,
        )
