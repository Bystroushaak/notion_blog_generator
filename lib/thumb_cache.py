import os
import shutil
import hashlib
import tempfile


class ThumbCache:
    allowed_types = {"jpg", "jpeg", "svg", "png"}
    name_randomizer = 0

    def __init__(self):
        self.tmp_dir = tempfile.mkdtemp()
        self.thumbs = {}

    @staticmethod
    def create_thumb_cache(blog_root):
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

        full_img_path = os.path.join(dirname, fn.replace("_thumb", ""))
        if os.path.exists(full_img_path):
            self.thumbs[self._get_hash(full_img_path)] = self._copy_to_tmp(path)
            return

        full_img_path = os.path.join(dirname, fn.replace("_thumb.jpg", ".jpeg"))
        if os.path.exists(full_img_path):
            self.thumbs[self._get_hash(full_img_path)] = self._copy_to_tmp(path)
            return

        full_img_path = os.path.join(dirname, fn.replace("_thumb.jpg", ".png"))
        if os.path.exists(full_img_path):
            self.thumbs[self._get_hash(full_img_path)] = self._copy_to_tmp(path)
            return

        full_img_path = os.path.join(dirname, fn.replace("_thumb.jpg", ".svg"))
        if os.path.exists(full_img_path):
            self.thumbs[self._get_hash(full_img_path)] = self._copy_to_tmp(path)
            return

    def try_restore(self, image_path):
        image_hash = self._get_hash(image_path)

        thumb_in_tmp = self.thumbs.get(image_hash)
        if thumb_in_tmp is not None:
            return self._copy_from_tmp(thumb_in_tmp, image_path)

        return None

    def _get_hash(self, path):
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    def _copy_to_tmp(self, path):
        subdir = self._make_subdir()

        tmp_name = os.path.join(self.tmp_dir, subdir, os.path.basename(path))
        shutil.copyfile(path, tmp_name)

        return tmp_name

    def _make_subdir(self):
        subdir = str(self.name_randomizer)
        self.name_randomizer += 1
        os.makedirs(os.path.join(self.tmp_dir, subdir), exist_ok=True)

        return subdir

    def _copy_from_tmp(self, tmp_name, image_path):
        fn = os.path.basename(tmp_name)
        dirname = os.path.dirname(image_path)
        thumb_path = os.path.join(dirname, fn)

        shutil.copyfile(tmp_name, thumb_path)

        return fn

    def __del__(self):
        self.cleanup()

    def cleanup(self):
        print("Thumb cache deleted.")
        if os.path.exists(self.tmp_dir):
            shutil.rmtree(self.tmp_dir)
