from lib.settings import settings

from .preprocessor_base import PreprocessorBase


class ConvertSpacesToUnderscores(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs, root):
        settings.logger.info("Converting all spaces in names to underscores..")

        for item in root.walk_all():
            item.filename = item.filename.replace(" ", "_")
            item.filename = item.filename.replace("%20", "_")
