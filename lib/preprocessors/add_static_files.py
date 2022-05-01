import os.path

from lib.settings import settings
from lib.virtual_fs import Data
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

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

    patreon_icon = None
    patreon_icon_ref = ""

    twitter_icon = None
    twitter_icon_ref = ""

    nginx_redirects = None
    nginx_redirects_ref = ""

    noto_font_subset_ttf = None
    noto_font_subset_ttf_ref = ""

    noto_font_subset_woff = None
    noto_font_subset_woff_ref = ""

    ads_txt = None
    ads_txt_ref = ""

    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
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

        cls.patreon_icon = cls._data_from_static_files("patreon.png")
        cls.patreon_icon_ref = registry.register_item_as_ref_str(cls.patreon_icon)

        cls.twitter_icon = cls._data_from_static_files("twitter_icon.png")
        cls.twitter_icon_ref = registry.register_item_as_ref_str(cls.twitter_icon)

        cls.nginx_redirects = cls._data_from_static_files("../nginx_redirects.txt")
        cls.nginx_redirects_ref = registry.register_item_as_ref_str(
            cls.nginx_redirects
        )

        cls.noto_font_subset_ttf = cls._data_from_static_files("NotoEmojiSubset.ttf")
        cls.noto_font_subset_ttf_ref = registry.register_item_as_ref_str(
            cls.noto_font_subset_ttf
        )
        cls.noto_font_subset_woff = cls._data_from_static_files("NotoEmojiSubset.woff")
        cls.noto_font_subset_woff_ref = registry.register_item_as_ref_str(
            cls.noto_font_subset_woff
        )

        cls.ads_txt = cls._data_from_static_files("ads.txt")
        cls.ads_txt_ref = registry.register_item_as_ref_str(cls.ads_txt)

        new_files = (
            cls.css,
            cls.js,
            cls.favicon,
            cls.rss_icon,
            cls.tweet_button,
            cls.patreon_icon,
            cls.twitter_icon,
            cls.nginx_redirects,
            cls.noto_font_subset_ttf,
            cls.noto_font_subset_woff,
            cls.ads_txt,
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
