from typing import Iterator

import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from lib.html_transformers.unroll_base import SubpageInfo
from lib.html_transformers.unroll_base import UnrollTraits


class UnrollCategories(UnrollTraits):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Unrolling categories into indexes ..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not page.is_index or not page.metadata.unroll_categories:
            return

        if not page.parent:
            return

        cls._unroll_category_to(virtual_fs.resource_registry, page)

    @classmethod
    def _unroll_category_to(cls, registry, page: HtmlPage):
        for category in cls.yield_subpages(page):
            category_si = list(cls._to_subpage_infos([category], registry))[0]
            subpages = cls._to_subpage_infos(cls.yield_subpages(category), registry)
            cls._insert_into(page, category_si, subpages)

    @classmethod
    def _to_subpage_infos(cls, pages_to_unroll, registry) -> Iterator[SubpageInfo]:
        description_template = '<p>%s</p>'

        for page in pages_to_unroll:
            page_ref = registry.register_item_as_ref_str(page)
            description_html = description_template % page.metadata.page_description

            yield SubpageInfo(page, page_ref, description_html)

    @classmethod
    def _insert_into(cls, target: HtmlPage, category: SubpageInfo,
                     subpages: Iterator[SubpageInfo]):
        subpages = list(subpages)

        for a_tag in target.dom.find("a"):
            href = a_tag.params.get("href")
            if href != category.ref_str:
                continue

            cls._insert_html_instead_of(a_tag, category, subpages)

    @classmethod
    def _insert_html_instead_of(cls, a_tag, category, subpages):
        html = cls._generate_html(category, subpages)
        a_tag.replaceWith(dhtmlparser.parseString(html))

    @classmethod
    def _generate_html(cls, category, subpages):
        subpages_htmls = [cls._subpage_to_html(subpage_info)
                          for subpage_info in subpages]

        html = """
        <h2><a href="{category_link}">{category_name}</a></h2>
        {subpages}
        """
        return html.format(category_name=category.page.title,
                           category_link=category.ref_str,
                           subpages="\n".join(subpages_htmls))

    @classmethod
    def _subpage_to_html(cls, subpage_info):
        date = subpage_info.page.metadata.date

        if date:
            link_html_template = (
                '<h4><a href="{link}">{name}</a> <time>(@{date})</time></h4>\n'
            )
            link_html = link_html_template.format(name=subpage_info.page.title,
                                                  link=subpage_info.ref_str,
                                                  date=date)
        else:
            link_html_template = '<h4><a href="{link}">{name}</a></h4>\n'
            link_html = link_html_template.format(name=subpage_info.page.title,
                                                  link=subpage_info.ref_str)

        return link_html + subpage_info.html
