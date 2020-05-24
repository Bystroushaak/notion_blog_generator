import os
import hashlib

from lib.settings import settings
from lib.create_abstract_tree import Data


class ThumbCache:
    allowed_types = {"jpg", "jpeg", "svg", "png"}
    name_randomizer = 0

    def __init__(self):
        self.thumbs = {}

    @staticmethod
    def create_thumb_cache(blog_root):
        settings.logger.info("Loading Thumbnail cache..")

        cache = ThumbCache()
        for root, dirs, files in os.walk(blog_root):
            for fn in files:
                cache.cache_thumb(os.path.join(root, fn))

        return cache

    def cache_thumb(self, path):
        fn = os.path.basename(path)
        dirname = os.path.dirname(path)

        if "_thumb." not in fn:
            return

        suffix = fn.rsplit(".", 1)[-1]

        if suffix not in self.allowed_types:
            return

        thumb_suffix = "_thumb.jpg"
        filename_variations = (
            fn.replace("_thumb", ""),
            fn.replace(thumb_suffix, ".jpeg"),
            fn.replace(thumb_suffix, ".png"),
            fn.replace(thumb_suffix, ".svg"),
        )

        for filename in filename_variations:
            full_img_path = os.path.join(dirname, filename)

            if os.path.exists(full_img_path):
                hash = self._get_hash_for_file(full_img_path)
                self.thumbs[hash] = self._import_thumbnail(path)
                return

    def _get_hash_for_file(self, path):
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _import_thumbnail(self, thumb_path):
        with open(thumb_path, "rb") as f:
            return Data(thumb_path, f.read())

    def try_restore(self, full_img: Data):
        image_hash = self._get_hash_for_bytes(full_img.content)
        return self.thumbs.get(image_hash, None)

    def _get_hash_for_bytes(self, data: bytes):
        return hashlib.md5(data).hexdigest()
