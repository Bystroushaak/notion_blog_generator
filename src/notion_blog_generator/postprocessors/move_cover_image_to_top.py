from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import Directory
from notion_blog_generator.virtual_fs import VirtualFS

from .postprocessor_base import PostprocessorBase


class MoveCoverImageToTop(PostprocessorBase):
    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Moving cover image above sidebar and breadcrumb..")

        for page in root.walk_htmls():
            cover_imgs = page.dom.find("img", {"class": "page-cover-image"})
            if not cover_imgs:
                continue

            cover = cover_imgs[0]
            cover.parent.remove(cover)

            body = page.dom.find("body")[0]
            body[0:] = cover
