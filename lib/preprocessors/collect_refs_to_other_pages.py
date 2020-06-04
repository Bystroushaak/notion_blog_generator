from lib.settings import settings
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .preprocessor_base import PreprocessorBase


class CollectRefsToOtherPages(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Collecting ref links to all pages..")

        registry = virtual_fs.resource_registry
        for page in root.walk_htmls():
            cls._collect_from(page, registry)

    @staticmethod
    def _collect_from(page, registry):
        if not page.is_embeddable:
            return

        own_ref_str = registry.register_item_as_ref_str(page)
        for link in page._collect_local_links():
            ref_str = link.params.get("href")
            if not ref_str:
                continue

            if not registry.is_ref_str(ref_str):
                continue

            item = registry.item_by_ref_str(ref_str)
            if not item.is_html:
                continue

            item.metadata.refs_from_other_pages.add(own_ref_str)
