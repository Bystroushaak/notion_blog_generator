from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class SidebarsAddBacklinks(TransformerBase):
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

        if not page.sidebar:
            return

        links_html = "\n".join(cls._yield_links(page))
        if not links_html:
            return

        page.sidebar.backlinks_html = f"""
        <div id="links_from_other_pages">
            <h3>Links to this page:</h3>
            <ul>
            {links_html}
            </ul>
        </div>
        """

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

            if "Změny" in parents or "Zmeny.html" in parents or "Zmeny" in parents:
                continue

            yield f'<li><a href="{ref}">{title}</a></li>'
