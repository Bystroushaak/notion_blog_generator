import sys
import logging

logger = logging.getLogger("objWiki")
stderr_logger = logging.StreamHandler(sys.stderr)
log_fmt = ("\033[90m%(asctime)s %(levelname)s %(filename)s:%(lineno)s;\033[0m\n"
           "%(message)s\n")
stderr_logger.setFormatter(logging.Formatter(log_fmt))
logger.addHandler(stderr_logger)
logger.setLevel(logging.DEBUG)


class Settings:
    def __init__(self):
        self.logger = logger


settings = Settings()
