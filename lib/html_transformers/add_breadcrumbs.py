import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddBreadcrumbs(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Breadcrumbs to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if page is root.inner_index:  # skip root index
            return

        bread_crumbs = cls._collect_parents_to_list(virtual_fs.resource_registry,
                                                    page)

        items = ["<a href='%s' class='breadcrumb'>%s</a>" % (ref_str, title)
                 for ref_str, title in bread_crumbs]
        items.append(page.title)

        all_items = " / ".join(items) + "\n\n"
        all_items_tag = dhtmlparser.parseString(all_items)

        page.dom.find("body")[0].childs.insert(0, all_items_tag)

    @classmethod
    def _collect_parents_to_list(cls, resource_registry, page):
        # index.html pages should link to parents and not themselves
        if page.parent and page.parent.inner_index is page:
            page = page.parent

        for item in reversed(list(cls.yield_parent_chain(page))):
            if item.parent and item.parent.inner_index is item:
                continue

            if item.is_directory and item.inner_index:
                item = item.inner_index

            ref_str = resource_registry.register_item_as_ref_str(item)
            yield ref_str, item.title

    @staticmethod
    def yield_parent_chain(page):
        page = page.parent  # start from the parent dir
        while page:
            yield page
            page = page.parent
