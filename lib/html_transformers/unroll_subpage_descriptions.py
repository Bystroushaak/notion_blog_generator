import re
from typing import Iterator
from collections import namedtuple

import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class SubpageInfo(namedtuple("SubpageInfo", "page ref_str html")):
    pass


class UnrollSubpageDescriptions(TransformerBase):
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
        pages_to_unroll = cls._get_pages_to_unroll(page)
        subpages_as_links = cls._pages_to_links(pages_to_unroll, registry)
        cls._insert_into(page, subpages_as_links)

    @classmethod
    def _get_pages_to_unroll(cls, page: HtmlPage):
        def sortkey(page):
            if not page.is_html:
                return ""

            if page.metadata.date:
                return page.metadata.date + page.title

            # for biweekly updates
            dates = re.findall(r"[\d]{4}[/-][\d]{2}[/-][\d]{2}", page.title)
            if dates:
                return dates[0].replace("/", "-")

            return page.title

        for file_in_dir in sorted(page.is_index_to.files, key=sortkey, reverse=True):
            if not file_in_dir.is_html:
                continue

            if file_in_dir is page:
                continue

            if file_in_dir is page.is_index_to.inner_index \
                or file_in_dir is page.is_index_to.outer_index:
                continue

            yield file_in_dir

    @classmethod
    def _pages_to_links(cls, pages_to_unroll, registry) -> Iterator[SubpageInfo]:
        description_template = '<p>%s</p><hr />'

        for page in pages_to_unroll:
            page_ref = registry.register_item_as_ref_str(page)
            page_html = description_template % page.metadata.page_description

            yield SubpageInfo(page, page_ref, page_html)

    @classmethod
    def _insert_into(cls, target: HtmlPage, subpages_as_links):
        subpages_as_links = list(subpages_as_links)
        ref_to_subpage_info = {si.ref_str: si for si in subpages_as_links}

        for a_tag in target.dom.find("a"):
            href = a_tag.params.get("href")
            subpage_info = ref_to_subpage_info.get(href)
            if subpage_info is None:
                continue

            date = subpage_info.page.metadata.date
            if date:
                link_html_template = '<h3><a href="%s">%s</a> <time>(%s)</time></h3>\n'
                link_html = link_html_template % (href, a_tag.getContent(),
                                                  date)
            else:
                link_html_template = '<h3><a href="%s">%s</a></h3>\n'
                link_html = link_html_template % (href, a_tag.getContent())

            a_tag.replaceWith(dhtmlparser.parseString(link_html + subpage_info.html))