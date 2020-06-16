from html import escape

import dhtmlparser

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
            head.childs.append(meta)

        if page.metadata.tags:
            meta = cls._add_meta_tag("keywords", ",".join(page.metadata.tags),
                                     escape_html=False)
            head.childs.append(meta)

        meta = cls._add_meta_tag("viewport", "width=device-width, initial-scale=1.0")
        head.childs.append(meta)

    @classmethod
    def _add_meta_tag(cls, name, content, escape_html=True):
        template = '<meta name="%s" content="%s" />'

        if escape_html:
            meta_str = template % (escape(name), escape(content))
        else:
            meta_str = template % (name, content)

        return dhtmlparser.parseString(meta_str).find("meta")[0]
