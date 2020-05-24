import sys
import logging

logger = logging.getLogger("objWiki")
stderr_logger = logging.StreamHandler(sys.stderr)
log_fmt = ("\033[90m%(asctime)s %(levelname)s %(filename)s:%(lineno)s;\033[0m\n"
           "%(message)s\n")
stderr_logger.setFormatter(logging.Formatter(log_fmt))
logger.addHandler(stderr_logger)
logger.setLevel(logging.INFO)


class Settings:
    def __init__(self):
        self.logger = logger
        self.blog_url = "http://blog.rfox.eu"
        self.patreon_url = "https://www.patreon.com/bePatron?u=2618881"
        self.atom_feed_url = "http://rfox.eu/raw/feeds/notion_blog.xml"
        self.google_analytics_code = "UA-142545439-1"

        self.twitter = "@Bystroushaak"
        self.twitter_url = ""

        self.number_of_articles_in_sidebar = 5
        self.number_of_articles_in_minichangelog = 5

        self.page_width = 900

    def check(self):
        if self.twitter and "@" not in self.twitter:
            self.twitter = "@" + self.twitter

        if self.twitter and not self.twitter_url:
            twitter_username = self.twitter.replace("@", "")
            self.twitter_url = "https://twitter.com/" + twitter_username


settings = Settings()
