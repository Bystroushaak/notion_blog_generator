import dhtmlparser3

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from lib.html_transformers.unroll_base import UnrollTraits


class UnrollSubpageDescriptions(UnrollTraits):
    @classmethod
    def log_transformer(cls):
        settings.logger.info(
            "Unrolling subsection descriptions unroll_subpages=True .."
        )

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not page.is_index or not page.metadata.unroll_subpages:
            return

        if not page.parent:
            return

        registry = virtual_fs.resource_registry
        cls._unroll_to(registry, page)

    @classmethod
    def _unroll_to(cls, registry, page: HtmlPage):
        pages_to_unroll = cls.yield_subpages(page)
        subpages_as_links = cls._to_subpage_infos(pages_to_unroll, registry)
        cls._insert_into(page, subpages_as_links)

    @classmethod
    def _insert_into(cls, target: HtmlPage, subpages_as_links):
        subpages_as_links = list(subpages_as_links)
        ref_to_subpage_info = {si.ref_str: si for si in subpages_as_links}

        for a_tag in target.dom.match(["figure", {"class": "link-to-page"}], "a"):
            href = a_tag.parameters.get("href")
            subpage_info = ref_to_subpage_info.get(href)
            if subpage_info is None:
                continue

            html = cls._subpage_to_html(subpage_info)
            a_tag.replace_with(dhtmlparser3.parse(html))
