from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory


class TransformerBase:
    requires = []
    did_run = False

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        pass

    @classmethod
    def log_transformer(cls):
        raise NotImplementedError()

    @classmethod
    def validate_requirements(cls):
        for requirement in cls.requires:
            if not requirement.did_run:
                raise ValueError(
                    "`%s` did not run yet and it is required by `%s`!" % (
                        requirement.__name__,
                        cls.__name__,
                    )
                )
