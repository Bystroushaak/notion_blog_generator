import re
from typing import Iterator
from collections import namedtuple

from jinja2 import Template

from lib.virtual_fs import HtmlPage

from lib.html_transformers.transformer_base import TransformerBase


class SubpageInfo(namedtuple("SubpageInfo", "page ref_str html")):
    pass


class UnrollTraits(TransformerBase):
    @classmethod
    def date_sortkey(cls, page: HtmlPage):
        if not page.is_html:
            return ""

        if page.metadata.date:
            return page.metadata.date + page.title

        # for biweekly updates
        dates = re.findall(r"[\d]{4}[/-][\d]{2}[/-][\d]{2}", page.title)
        if dates:
            return dates[0].replace("/", "-")

        return page.title

    @classmethod
    def yield_subpages(cls, page: HtmlPage):
        if not page.is_index_to:
            return

        for file_in_dir in sorted(page.is_index_to.files, key=cls.date_sortkey,
                                  reverse=True):
            if not file_in_dir.is_html:
                continue

            if file_in_dir is page:
                continue

            if file_in_dir is page.is_index_to.inner_index \
                or file_in_dir is page.is_index_to.outer_index:
                continue

            yield file_in_dir

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
        """
        If the date is not found, look for it in the subpages. Useful for
        categories.

        Also return number of subpages, one level deep.

        Returns:
            tuple: (date from subpage, number of subpages)
        """
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
    def _subpage_to_html(cls, subpage_info, add_div=False):
        number_of_subsubpages = subpage_info.page.metadata.number_of_subsubpages

        jinja_template = Template("""
{% if add_div: %}
<div style="margin-left: 1em">
{% endif %}
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
{% if add_div: %}
</div>
{% endif %}
""")
        return jinja_template.render(date=subpage_info.page.metadata.date,
                                     last_mod=subpage_info.page.metadata.last_mod,
                                     page=subpage_info.page,
                                     link=subpage_info.ref_str,
                                     description=subpage_info.html,
                                     number_of_subsubpages=number_of_subsubpages,
                                     add_div=add_div)
