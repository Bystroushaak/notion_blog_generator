from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory


class TransformerBase:
    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        pass

    @classmethod
    def log_transformer(cls):
        raise NotImplementedError()
