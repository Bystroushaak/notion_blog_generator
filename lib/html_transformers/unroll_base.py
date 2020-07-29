import re
from collections import namedtuple

from lib.html_transformers.transformer_base import TransformerBase
from lib.virtual_fs import HtmlPage


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
