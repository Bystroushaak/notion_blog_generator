from lib.settings import settings
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .preprocessor_base import PreprocessorBase


class RenameRootSections(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Renaming `English_section/` to `en/` and "
                             "`Czech_section/` to `cz/`.")

        for dir in root.subdirs:
            if dir.filename == "English_section":
                dir.filename = "en"
            if dir.filename == "Czech_section":
                dir.filename = "cz"
