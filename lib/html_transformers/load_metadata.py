import html

import yaml
import dhtmlparser

from lib.settings import settings

from .transformer_base import TransformerBase

from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS
from lib.virtual_fs.html_page import HtmlPage
from lib.virtual_fs.html_page import Metadata


class LoadMetadata(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Loading metadata from all HTML pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        made_doublelinked = False
        for code_tag in page.dom.match(["pre", {"class": "code"}], "code"):
            code_content = html.unescape(code_tag.getContent())
            code_content_lines = code_content.splitlines()

            if code_content_lines and code_content_lines[0] == "#lang:metadata":
                page.metadata = Metadata.from_yaml("\n".join(code_content_lines[1:]))

                if not made_doublelinked:
                    dhtmlparser.makeDoubleLinked(page.dom)
                    made_doublelinked = True

                code_tag.parent.replaceWith(dhtmlparser.parseString(""))
