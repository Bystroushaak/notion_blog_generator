from lib.settings import settings
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

    @staticmethod
    def _to_abs_url_path(resource_relpath):
        blog_url = settings.blog_url

        if not blog_url.endswith("/") and not resource_relpath.startswith("/"):
            blog_url += "/"

        return blog_url + resource_relpath
