from lib.settings import settings
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory
from lib.virtual_fs import RootSection

from .preprocessor_base import PreprocessorBase


class MakeRootSections(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Renaming `English_section/` to `en/` and "
                             "`Czech_section/` to `cz/`.")

        root.subdirs = list(cls._reindex_dirs(root))

    @classmethod
    def _reindex_dirs(cls, root):
        for dir in root.subdirs:
            if dir.filename == "English_section":
                dir.filename = "en"
                yield RootSection.make_from(dir)
            elif dir.filename == "Czech_section":
                dir.filename = "cz"
                yield RootSection.make_from(dir)
            else:
                yield dir
