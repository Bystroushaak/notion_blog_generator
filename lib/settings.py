import sys
import os.path
import logging

logger = logging.getLogger("NotionBloggenerator")
stderr_logger = logging.StreamHandler(sys.stderr)
log_fmt = (
    "\033[90m%(asctime)s %(levelname)s %(filename)s:%(lineno)s;\033[0m\n"
    "%(message)s\n"
)
stderr_logger.setFormatter(logging.Formatter(log_fmt))
logger.addHandler(stderr_logger)
logger.setLevel(logging.INFO)


class ThumbFormat:
    PNG = "PNG"
    JPG = "JPEG"

    @staticmethod
    def thumb_format_to_suffix(format):
        if format == ThumbFormat.PNG:
            return "png"
        elif format == ThumbFormat.JPG:
            return "jpg"
        else:
            raise ValueError(f"Invalid thumb format: `{format}`")


class Settings:
    def __init__(self):
        self.logger = logger
        self.blog_url = "https://blog.rfox.eu"
        self.blog_name = "Bystroushaak's blog"
        self.patreon_url = "https://www.patreon.com/bePatron?u=2618881"
        self.google_analytics_code = "UA-142545439-1"
        self.google_adsense_code = "ca-pub-8322439660353685"

        self.twitter_url = ""
        self.twitter_handle = "@Bystroushaak"

        self.number_of_articles_in_sidebar = 10
        self.number_of_articles_in_minichangelog = 5

        self.unrolls_enabled = True
        self.number_of_subpages_in_unroll = 3
        self.unrolls_with_descriptions = False  # can be allowed by page metadata

        self.page_width = 1200
        self.thumb_format = ThumbFormat.JPG

        self.generate_thumbnails = True
        self.thumb_cache_name = ".thumb_cache"

        self.tidy_html = True
        self.write_prettify = False

        self.generated_feed_name = "atom.xml"
        self.atom_feed_root_url = self.blog_url + "/"
        self.number_of_items_in_feed = 10

        self.lang_classificator_enabled = False

        self.notion_token_path = os.path.expanduser("~/.config/notion_api/blog.txt")
        self.notion_api_token = self._load_token()

        self.check()

    def check(self):
        if self.twitter_handle and "@" not in self.twitter_handle:
            self.twitter_handle = "@" + self.twitter_handle

        if self.twitter_handle and not self.twitter_url:
            twitter_username = self.twitter_handle.replace("@", "")
            self.twitter_url = "https://twitter.com/" + twitter_username

    def _load_token(self):
        if os.path.exists(self.notion_token_path):
            self.logger.info("Notion token loaded from `%s`.", self.notion_token_path)
            with open(self.notion_token_path) as f:
                return f.read().strip()


settings = Settings()
