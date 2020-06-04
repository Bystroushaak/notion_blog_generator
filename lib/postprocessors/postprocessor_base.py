from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS


class PostprocessorBase:
    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
        pass
