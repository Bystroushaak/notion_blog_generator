from lib.settings import settings

from .preprocessor_base import PreprocessorBase


class RenameRootSections(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs, root):
        settings.logger.info("Renaming `English_section/` to `en/` and "
                             "`Czech_section/` to `cz/`.")

        for dir in root.subdirs:
            if dir.filename == "English_section":
                dir.filename = "en"
            if dir.filename == "Czech_section":
                dir.filename = "cz"
