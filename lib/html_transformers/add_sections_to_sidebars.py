import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase
from .unroll_base import UnrollTraits


class AddSectionsToSidebars(TransformerBase):
    section_to_html_map = {}

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding section links to sidebars..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not page.sidebar:
            return

        root_section = page.root_section
        html = cls.section_to_html_map.get(id(root_section))
        if html:
            page.sidebar.sections_html = html
            return

        html = '<div>\n<h3>Blog categories</h3>\n<ul class="no_icon">'
        for page_link in cls._yield_links(root_section, virtual_fs):
            html += page_link
        html += "</ul>\n</div>\n"

        cls.section_to_html_map[id(root_section)] = html
        page.sidebar.sections_html = html

    @classmethod
    def _yield_links(cls, root_section, virtual_fs):
        subpage_infos = UnrollTraits._to_subpage_infos(root_section.files,
                                                       virtual_fs.resource_registry)
        for subpage_info in subpage_infos:
            title = subpage_info.page.icon + " " + subpage_info.page.title
            yield '  <li><a href="%s">%s</a></li>\n' % (subpage_info.ref_str, title)
