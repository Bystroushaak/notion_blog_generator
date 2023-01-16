import os.path
from typing import List, Optional
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

            cls._replace_with_file_link(virtual_fs, page, figure, href, figcaption)

    @classmethod
    def _replace_with_file_link(
        cls,
        virtual_fs: VirtualFS,
        page: HtmlPage,
        figure_el: Tag,
        href: str,
        figcaption: List[Tag],
    ):
        ref_str = cls._look_for_file(virtual_fs, page, href)

        if figcaption and not ref_str:
            href = cls._parse_figcaption(figcaption[0])

        link_el = Tag("p")
        link_el[0:] = Tag(
            "a", parameters={"href": ref_str or href}, content=[f"📎 {cls._get_name(href)}"]
        )

        figure_el.replace_with(link_el)

    @classmethod
    def _look_for_file(cls, virtual_fs: VirtualFS, page: HtmlPage, href: str) -> Optional[str]:
        filename = cls._get_name(href)

        if not page.is_index_to:
            return None

        matching_fns = [x for x in page.is_index_to.files if x.filename == filename]
        if not matching_fns:
            return None

        file_obj = matching_fns[0]
        return virtual_fs.resource_registry.register_item_as_ref_str(file_obj)

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
