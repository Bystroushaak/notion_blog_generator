from lib.settings import settings
from lib.virtual_fs.resource_registry import ResourceRegistry

from .postprocessor_base import PostprocessorBase


class ConvertTwitterCardsToAbsURL(PostprocessorBase):
    @classmethod
    def postprocess(cls, virtual_fs, root):
        settings.logger.info("Converting twitter cards to abs url..")

        for page in root.walk_htmls():
            for meta in page.dom.find("meta", {"name": "twitter:image"}):
                resource_id_token = meta.params["content"]
                if not ResourceRegistry.is_ref_str(resource_id_token):
                    continue

                resource = virtual_fs.resource_registry.item_by_ref_str(resource_id_token)
                abs_path = cls._to_abs_url_path(resource.path)
                meta.params["content"] = abs_path

    @staticmethod
    def _to_abs_url_path(resource_relpath):
        image_path = settings.blog_url

        if not settings.blog_url.endswith("/") and not resource_relpath.startswith("/"):
            image_path += "/"

        return image_path + resource_relpath
