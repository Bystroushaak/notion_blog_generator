import os.path

from lib.settings import settings
from lib.virtual_fs import Data

from .preprocessor_base import PreprocessorBase


class AddStaticFiles(PreprocessorBase):
    _static_dir_path = os.path.join(os.path.dirname(__file__),
                                    "../../static_files")

    css = None
    css_ref = ""

    js = None
    js_ref = ""

    favicon = None
    favicon_ref = ""

    rss_icon = None
    rss_icon_ref = ""

    tweet_button = None
    tweet_button_ref = ""

    twitter_icon = None
    twitter_icon_ref = ""

    nginx_redirects = None
    nginx_redirects_ref = ""

    @classmethod
    def preprocess(cls, virtual_fs, root):
        settings.logger.info("Adding static files to virtual filesystem..")

        registry = virtual_fs.resource_registry

        cls.css = cls._data_from_static_files("custom_style.css", "style.css")
        cls.css_ref = registry.register_item_as_ref_str(cls.css)

        cls.js = cls._data_from_static_files("scripts.js")
        cls.js_ref = registry.register_item_as_ref_str(cls.js)

        cls.favicon = cls._data_from_static_files("favicon.ico")
        cls.favicon_ref = registry.register_item_as_ref_str(cls.favicon)

        cls.rss_icon = cls._data_from_static_files("rss_icon.png")
        cls.rss_icon_ref = registry.register_item_as_ref_str(cls.rss_icon)

        cls.tweet_button = cls._data_from_static_files("tweet_button.svg")
        cls.tweet_button_ref = registry.register_item_as_ref_str(cls.tweet_button)

        cls.twitter_icon = cls._data_from_static_files("twitter_icon.png")
        cls.twitter_icon_ref = registry.register_item_as_ref_str(cls.twitter_icon)

        cls.nginx_redirects = cls._data_from_static_files("../nginx_redirects.txt")
        cls.nginx_redirects_ref = registry.register_item_as_ref_str(cls.nginx_redirects)

        new_files = (
            cls.css,
            cls.js,
            cls.favicon,
            cls.rss_icon,
            cls.tweet_button,
            cls.twitter_icon,
            cls.nginx_redirects,
        )

        for file in new_files:
            root.files.append(file)
            file.parent = root

    @classmethod
    def _data_from_static_files(cls, fn, new_fn=None):
        path = os.path.join(cls._static_dir_path, fn)

        if not new_fn:
            new_fn = fn

        with open(path, "rb") as f:
            return Data(new_fn, f.read())
