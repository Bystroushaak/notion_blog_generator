import os.path
from typing import List
from urllib.parse import urlparse

from dhtmlparser3 import Tag

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class FixFileUploads(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Fixing file uploads (adding link, renaming) ..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        for figure in page.dom.find("figure"):
            source_div = figure.find("div", {"class": "source"})
            if not source_div:
                continue

            figcaption = figure.find("figcaption")

            first_div = source_div[0]

            links = first_div.find("a")
            if not links:
                continue

            first_link = links[0]
            href = first_link.content_str().strip()

            if not href.startswith("http"):
                continue

            cls._replace_with_file_link(figure, href, figcaption)

    @classmethod
    def _replace_with_file_link(
        cls,
        figure_el: Tag,
        href: str,
        figcaption: List[Tag],
    ):
        if figcaption:
            href = cls._parse_figcaption(figcaption[0])

        link_el = Tag("p")
        link_el[0:] = Tag(
            "a", parameters={"href": href}, content=[f"📎 {cls._get_name(href)}"]
        )

        figure_el.replace_with(link_el)

    @classmethod
    def _parse_figcaption(cls, figcaption: Tag) -> str:
        """
        Because notion retards removed access to aws files, and API doesn't
        support downloading files (not even unofficial ones).

        TODO: check sometime in future: https://developers.notion.com/reference/block
        """
        return figcaption.find("a")[0]["href"]

    @classmethod
    def _get_name(cls, href: str) -> str:
        parsed_url = urlparse(href)
        return os.path.basename(parsed_url.path)
