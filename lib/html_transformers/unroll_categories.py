from typing import Iterator

import dhtmlparser
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
    def _to_subpage_infos(cls, subpages, registry) -> Iterator[SubpageInfo]:
        for page in subpages:
            page_ref = registry.register_item_as_ref_str(page)
            description = page.metadata.page_description
            if not description:
                description = "&nbsp;"

            subpage_info = SubpageInfo(page, page_ref, description)

            date, number_of_subsubpages = cls._date_from_subsubpage(subpage_info)
            page.metadata.date = date
            page.metadata.number_of_subsubpages = number_of_subsubpages

            yield subpage_info


    @classmethod
    def _date_from_subsubpage(cls, subpage_info):
        def is_not_inner_index(page):
            if not page.is_index:
                return True

            if page.is_index_to.inner_index is not page:
                return True

            return False

        date = subpage_info.page.metadata.date
        number_of_subsubpages = 0
        if subpage_info.page.is_category:
            subsubpages = subpage_info.page.is_index_to.files
            number_of_subsubpages = len([x for x in subsubpages
                                         if x.is_html and is_not_inner_index(x)])

            if not date:
                dates = sorted([subpage.metadata.date
                                for subpage in subsubpages
                                if subpage.is_html and subpage.metadata.date])
                if dates:
                    date = dates[-1]

        return date, number_of_subsubpages

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
            href = a_tag.params.get("href")
            if href != category.ref_str:
                continue

            cls._insert_html_instead_of(a_tag, category, subpages, and_more)

    @classmethod
    def _insert_html_instead_of(cls, a_tag, category, subpages, and_more=0):
        html = cls._generate_html(category, subpages, and_more)
        a_tag.replaceWith(dhtmlparser.parseString(html))

    @classmethod
    def _generate_html(cls, category, subpages, and_more):
        subpages_htmls = [cls._subpage_to_html(subpage_info)
                          for subpage_info in subpages]

        jinja_template = Template("""
<h1><a href="{{ category_link }}" class="unroll_category">
    Category: <em>{{ category_name }}</em></a></h1>
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

    @classmethod
    def _subpage_to_html(cls, subpage_info):
        number_of_subsubpages = subpage_info.page.metadata.number_of_subsubpages

        jinja_template = Template("""
<div style="margin-left: 1em">
<h4><a href="{{ link }}" class="">{{ page.icon }} {{ page.title }}</a>
{% if number_of_subsubpages > 0 %}
    {% if date: %}
        <time>(last update @{{ date }},
    {% else: %}
        <time>(
    {% endif %}
    {{ number_of_subsubpages }}
        {% if number_of_subsubpages > 1 %}
            subpages)</time>
        {% else %}
            subpage)</time>
        {% endif %}
{% else %}
    {% if last_mod: %}
        <time>(last modified @{{ last_mod }})</time>
    {% else: %}
        {% if date: %} <time>(@{{ date }})</time>{% endif %}
    {% endif %}
{% endif %}
</h4>
<p style="margin-top: -1em;"><em>{{ description }}</em></p>
</div>
""")
        return jinja_template.render(date=subpage_info.page.metadata.date,
                                     last_mod=subpage_info.page.metadata.last_mod,
                                     page=subpage_info.page,
                                     link=subpage_info.ref_str,
                                     description=subpage_info.html,
                                     number_of_subsubpages=number_of_subsubpages)
