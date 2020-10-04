from lib.settings import settings
from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS

from .postprocessor_base import PostprocessorBase


class AddSidebarsToAllPages(PostprocessorBase):
    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Adding sidebars to all pages..")

        for page in root.walk_htmls():
            if not page.is_embeddable:
                page.sidebar = None
                continue

            if page.sidebar is not None:
                page.sidebar.add_to_page(page, root)

    @classmethod
    def is_sidebarable(cls, page, root):
        if not page.is_embeddable:
            return False

        if page is root.outer_index or page is root.inner_index:
            return False

        return True

