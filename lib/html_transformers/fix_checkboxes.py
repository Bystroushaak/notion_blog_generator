from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class FixCheckboxes(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Fixing checkboxes..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        for span in page.dom.find("span", {"class": "to-do-children-unchecked"}):
            span[0:] = "☐ "
