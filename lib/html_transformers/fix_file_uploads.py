import os.path
from typing import List
from urllib.parse import urlparse

import dhtmlparser

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
            href = first_link.getContent().strip()

            if not href.startswith("http"):
                continue

            cls._replace_with_file_link(figure, href, figcaption)

    @classmethod
    def _replace_with_file_link(
        cls,
        figure_el: dhtmlparser.HTMLElement,
        href: str,
        figcaption: List[dhtmlparser.HTMLElement],
    ):
        if figcaption:
            href = cls._parse_figcaption(figcaption[0])

        link_html = f'<p><a href="{href}">📎 {cls._get_name(href)}</a></p>'
        link_el = dhtmlparser.parseString(link_html).find("p")[0]

        figure_el.replaceWith(link_el)

    @classmethod
    def _parse_figcaption(cls, figcaption):
        """
        Because notion retards removed access to aws files, and API doesn't
        support downloading files (not even unofficial ones).

        TODO: check sometime in future: https://developers.notion.com/reference/block
        """
        return figcaption.find("a")[0].params["href"]

    @classmethod
    def _get_name(cls, href):
        parsed_url = urlparse(href)
        return os.path.basename(parsed_url.path)
