from lib.settings import settings
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .preprocessor_base import PreprocessorBase
from .unfuck_filenames import UnfuckFilenames


class ConvertSpacesToUnderscores(PreprocessorBase):
    requires = [UnfuckFilenames]

    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Converting all spaces in names to underscores..")

        for item in root.walk_all():
            item.filename = item.filename.replace(" ", "_")
            item.filename = item.filename.replace("%20", "_")
