from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory


class PreprocessorBase:
    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        pass
