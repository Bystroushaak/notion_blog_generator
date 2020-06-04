import os.path

from lib.settings import settings
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .preprocessor_base import PreprocessorBase


class GenerateIndexesForDirectories(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Generating indexes for directories..")

        for dir, file in cls.all_dirs_that_contain_html_with_same_name(root):
            dir.add_copy_as_index(file)

    @classmethod
    def all_dirs_that_contain_html_with_same_name(cls, root):
        for dir in root.walk_dirs():
            dirname = os.path.basename(dir.path).strip()

            if not dir.parent:
                continue

            yield from cls._files_with_dirname(dir, dirname)

    @classmethod
    def _files_with_dirname(cls, dir, dirname):
        for file in dir.parent.files:
            filename = os.path.basename(file.filename)
            if "." in filename:
                filename = filename.rsplit(".", 1)[0].strip()

            if dirname == filename:
                yield dir, file
