import os
import hashlib

from lib.settings import settings
from lib.virtual_fs import Data


class ThumbCache:
    allowed_types = {"jpg", "jpeg", "svg", "png"}

    def __init__(self):
        self.hash_to_thumb_map = {}

    @staticmethod
    def _instance(blog_root):
        return ThumbCache()

    @classmethod
    def create_thumb_cache(cls, blog_root):
        settings.logger.info("Loading %s cache..", cls.__name__)

        cache = cls._instance(blog_root)
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

            if not os.path.exists(full_img_path):
                continue

            hash = self._get_hash_for_file(full_img_path)
            if hash in self.hash_to_thumb_map:
                return

            self.hash_to_thumb_map[hash] = self._import_thumbnail(path)
            return

    def _get_hash_for_file(self, path):
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _import_thumbnail(self, thumb_path):
        with open(thumb_path, "rb") as f:
            return Data(thumb_path, f.read())

    def try_restore(self, full_img: Data):
        image_hash = self._get_hash_for_bytes(full_img.content)
        return self.hash_to_thumb_map.get(image_hash, None)

    def _get_hash_for_bytes(self, data: bytes):
        return hashlib.md5(data).hexdigest()


class StoredThumbCache(ThumbCache):
    def __init__(self, storage_path):
        super().__init__()

        self.storage_path = storage_path
        self.load_from_storage()

    @staticmethod
    def _instance(blog_root):
        return StoredThumbCache(os.path.join(blog_root, settings.thumb_cache_name))

    def load_from_storage(self, storage_path=None):
        if not storage_path:
            storage_path = self.storage_path

        if not os.path.exists(storage_path):
            return

        settings.logger.info("Loading thumbnails from cache dir `%s`..", storage_path)

        metadata = {}
        for fn in os.listdir(storage_path):
            path = os.path.join(storage_path, fn)

            if fn.endswith(".txt"):
                with open(path, "rt") as f:
                    metadata[fn.rsplit(".txt", 1)[0]] = f.read().strip()
            else:
                with open(path, "rb") as f:
                    self.hash_to_thumb_map[fn] = Data("None", f.read())

        for hash, filename in metadata.items():
            self.hash_to_thumb_map[hash].filename = filename

    def save_to_storage(self, storage_path=None):
        if not storage_path:
            storage_path = self.storage_path

        settings.logger.info("Storing thumbnail cache in `%s`..", storage_path)

        os.makedirs(storage_path, exist_ok=True)

        for hash, item in self.hash_to_thumb_map.items():
            thumb_name = os.path.join(storage_path, hash)

            if os.path.exists(thumb_name):
                continue

            with open(thumb_name, "wb") as f:
                f.write(item.content)

            metadata_name = os.path.join(storage_path, hash + ".txt")
            with open(metadata_name, "wt") as f:
                f.write(item.filename)
