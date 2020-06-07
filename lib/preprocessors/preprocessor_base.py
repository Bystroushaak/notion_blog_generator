from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory


class PreprocessorBase:
    requires = []
    did_run = False

    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        pass

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
