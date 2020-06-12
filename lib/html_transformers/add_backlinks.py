import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase
from .add_sidebars import AddSidebarsToAllPages


class AddBacklinks(TransformerBase):
    requires = [AddSidebarsToAllPages]

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding table with backlinks to all HTML pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not page.is_embeddable:
            return

        cls._add_backlinks_to(page)

    @classmethod
    def _add_backlinks_to(cls, page):
        if not page.metadata.refs_from_other_pages:
            return

        html = """
        <div id="links_from_other_pages">
            <h3>Links to this page:</h3>
            <ul>
            %s
            </ul>
        </div>
        """
        links_code = "\n".join(cls._yield_links(page))

        if not links_code:
            return

        top_code = html % links_code
        top_tag = dhtmlparser.parseString(top_code).find("div")[0]
        top_div = page.dom.find("div", {"id": "sidebar_top"})[0]
        top_div.childs.append(top_tag)

        bottom_code = html % links_code
        bottom_tag = dhtmlparser.parseString(bottom_code).find("div")[0]
        bottom_div = page.dom.find("div", {"id": "sidebar_bottom"})[0]
        bottom_div.childs.append(bottom_tag)

    @classmethod
    def _yield_links(cls, page):
        sorted_refs = sorted(page.metadata.refs_from_other_pages,
                             key=lambda x: x.item.metadata.date or x.title)

        for ref, title, item in sorted_refs:
            if page.parent.inner_index is item or page.parent.outer_index is item:
                continue

            # Pages in Changelog dir should be ignored
            parents = set(x.filename for x in item.yield_parents())
            parents.add(item.filename)
            if "Changelog" in parents or "Changelog.html" in parents:
                continue

            yield '<li><a href="%s">%s</a></li>' % (ref, title)