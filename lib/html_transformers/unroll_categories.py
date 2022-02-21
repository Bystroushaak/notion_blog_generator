from typing import Iterator

import dhtmlparser3
from jinja2 import Template

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
    def _insert_into(cls, target: HtmlPage, category: SubpageInfo,
                     subpages: Iterator[SubpageInfo]):
        limit = 10
        limit_to = 3
        and_more = 0
        subpages = list(subpages)
        if len(subpages) > limit:
            and_more = len(subpages) - limit_to
            subpages = subpages[:limit_to]

        for a_tag in target.dom.find("a"):
            href = a_tag.parameters.get("href")
            if href != category.ref_str:
                continue

            cls._insert_html_instead_of(a_tag, category, subpages, and_more)

    @classmethod
    def _insert_html_instead_of(cls, a_tag, category, subpages, and_more=0):
        html = cls._generate_html(category, subpages, and_more)
        a_tag.replace_with(dhtmlparser3.parse(html))

    @classmethod
    def _generate_html(cls, category, subpages, and_more):
        subpages_htmls = [cls._subpage_to_html(subpage_info, add_div=True)
                          for subpage_info in subpages]

        jinja_template = Template("""
<h1><a href="{{ category_link }}" class="unroll_category">
    📂 <u>Category: <em>{{ category_name }}</em></u>
</a></h1>
{{ subpages }}
{% if and_more > 0: %}
<h4 style="text-align: right;"><a href="{{ category_link }}">
    {% if and_more > 1: %}
        & {{ and_more }} more blogposts
    {% else: %}
        & 1 more blogpost
    {% endif %}
</a></h4>
{% endif %}
""")

        return jinja_template.render(category_link=category.ref_str,
                                     category_name=category.page.title,
                                     subpages="\n".join(subpages_htmls),
                                     and_more=and_more)

