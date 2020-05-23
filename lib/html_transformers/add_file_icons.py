import dhtmlparser

from lib.settings import settings

from .transformer_base import TransformerBase


class AddFileIcons(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding file icons to all pages..")

    @classmethod
    def transform(cls, virtual_fs, root, page):
        file_icon_str = '<span class="icon">🗎</span>'
        file_icon_tag = dhtmlparser.parseString(file_icon_str).find("span")[0]

        for figure in page.dom.find("figure", {"class": "link-to-page"}):
            if figure.find("span", {"class": "icon"}):
                continue

            a = figure.find("a")
            if not a:
                continue

            a[0].childs.insert(0, file_icon_tag)
