from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .preprocessor_base import PreprocessorBase


class SquashToplevelDirectory(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Squashing toplevel directory..")

        root_index = root.files[0]
        root_index.filename = "index.html"

        # squash toplevel directory, as it holds only index
        blog_subdir = root.subdirs[0]
        root.subdirs = blog_subdir.subdirs
        root.files = blog_subdir.files
        root.files.append(root_index)
        root.reindex_parents()

        root.inner_index = root_index
        root.outer_index = root_index
