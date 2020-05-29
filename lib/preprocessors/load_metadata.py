import html

import dhtmlparser

from lib.settings import settings

from .preprocessor_base import PreprocessorBase

from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS
from lib.virtual_fs.html_page import Metadata


class LoadMetadata(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Loading metadata from all HTML pages..")

        for page in root.walk_htmls():
            cls.parse_metadata_in_page(page)

    @classmethod
    def parse_metadata_in_page(cls, page):
        dhtmlparser.makeDoubleLinked(page.dom)

        for code_tag in page.dom.match(["pre", {"class": "code"}], "code"):
            code_content = html.unescape(code_tag.getContent())
            code_content_lines = code_content.splitlines()

            if code_content_lines and code_content_lines[0] == "#lang:metadata":
                page.metadata = Metadata.from_yaml("\n".join(code_content_lines[1:]))
                code_tag.parent.replaceWith(dhtmlparser.parseString(""))

        page.metadata.page_description = cls._parse_description(page)

    @classmethod
    def _parse_description(cls, page):
        p_tags = page.dom.match(
            "body",
            {"tag_name": "div", "params": {"class": "page-body"}},
            "p"
        )

        possible_descriptions = [
            dhtmlparser.removeTags(p.getContent())
            for p in p_tags if not cls._is_unwanted_element(p)
        ]
        if possible_descriptions:
            return possible_descriptions[0]

        return ""

    @staticmethod
    def _is_unwanted_element(p):
        if p.find("time"):
            return True

        if p.params.get("class") == "column":
            return True

        if len(dhtmlparser.removeTags(p.getContent())) <= 30:
            return True

        if p.parent.params.get("class") != "page-body":
            return True

        return False
