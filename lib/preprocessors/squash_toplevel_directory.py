from lib.settings import settings

from .preprocessor_base import PreprocessorBase


class SquashToplevelDirectory(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs, root):
        root_index = root.files[0]
        root_index.filename = "index.html"

        # squash toplevel directory, as it holds only index
        blog_subdir = root.subdirs[0]
        root.subdirs = blog_subdir.subdirs
        root.files = blog_subdir.files
        root.files.append(root_index)
        root.reindex_parents()

        settings.logger.info("Toplevel directory squashed.")
