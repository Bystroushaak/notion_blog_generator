from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS


class PostprocessorBase:
    requires = []
    did_run = False

    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
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
