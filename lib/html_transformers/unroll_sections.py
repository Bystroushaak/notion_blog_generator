import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class UnrollSections(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Unrolling articles in sections with unroll=True ..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not page.is_index or not page.metadata.unroll:
            return

        if not page.parent:
            return

        registry = virtual_fs.resource_registry
        cls._unroll_to(registry, page, page.parent.inner_index)
        cls._unroll_to(registry, page, page.parent.outer_index)

    @classmethod
    def _unroll_to(cls, registry, page: HtmlPage, directory_page: HtmlPage):
        pages_to_unroll = cls._get_pages_to_unroll(page)
        subpages_as_links = cls._pages_to_links(pages_to_unroll, registry,
                                                page.metadata.unroll_description)

        page_ref_str = registry.register_item_as_ref_str(page)
        cls._insert_into(directory_page, page_ref_str, subpages_as_links)

    @classmethod
    def _get_pages_to_unroll(cls, page: HtmlPage):
        for file_in_dir in page.is_index_to.files:
            if not file_in_dir.is_html:
                continue

            if file_in_dir is page:
                continue

            if file_in_dir is page.is_index_to.inner_index \
                or file_in_dir is page.is_index_to.outer_index:
                continue

            yield file_in_dir

    @classmethod
    def _insert_into(cls, target: HtmlPage, page_ref_str, subpages_as_links):
        def find_links_to_the_subsection(x):
            return x.params.get("href") == page_ref_str

        links = target.dom.find("a", fn=find_links_to_the_subsection)
        if not links:
            return

        link = links[0]

        subpages_as_links = list(subpages_as_links)
        if not subpages_as_links:
            return

        more = 0
        max_unroll = settings.number_of_subpages_in_unroll
        if len(subpages_as_links) > max_unroll:
            more = len(subpages_as_links) - max_unroll
            subpages_as_links = subpages_as_links[:max_unroll]

        else:
            last_unroll = subpages_as_links[-1]
            last_unroll = last_unroll.replace("<li>", '<li class="unroll_last">', 1)
            subpages_as_links[-1] = last_unroll

        subpages_html = "\n".join(subpages_as_links)
        if more > 0:
            fmt_str = '\n<li class="unroll_last"><a href="%s">.. & %d more</a></li>\n'
            subpages_html += fmt_str % (page_ref_str, more)

        link_html = '<a href="%s">%s</a>\n' % (page_ref_str, link.getContent())
        subpages_html = '<ul class="unroll">\n%s\n</ul>\n' % subpages_html

        link.replaceWith(dhtmlparser.parseString(link_html + subpages_html))

    @classmethod
    def _pages_to_links(cls, pages_to_unroll, registry, show_description):
        template = '<li><a href="%s">%s</a></li>'
        description_template = '<li><a href="%s">%s</a><br>%s</li>'

        for page in pages_to_unroll:
            page_ref = registry.register_item_as_ref_str(page)

            if show_description:
                yield description_template % (page_ref, page.title,
                                              page.metadata.page_description)
            else:
                yield template % (page_ref, page.title)
