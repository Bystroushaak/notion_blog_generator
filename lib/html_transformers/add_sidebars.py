import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS

from .transformer_base import TransformerBase


class AddSidebarsToAllPages(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding sidebars to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not page.is_embeddable:
            return

        cls._add_sidebars_to_page(page)

    @classmethod
    def is_sidebarable(cls, page, root):
        if not page.is_embeddable:
            return False

        if page is root.outer_index or page is root.inner_index:
            return False

        return True

    @classmethod
    def _add_sidebars_to_page(cls, page):
        top_tag_code = """<div id="sidebar_top">

<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-8322439660353685"
     data-ad-slot="8589969791"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
</div>"""
        bottom_tag_code = '<div id="sidebar_bottom">\n</div>'

        top_tag = dhtmlparser.parseString(top_tag_code).find("div")[0]
        bottom_tag = dhtmlparser.parseString(bottom_tag_code).find("div")[0]

        body_tag = page.dom.find("body")[0]
        body_tag.childs.insert(0, top_tag)
        body_tag.childs.append(bottom_tag)
