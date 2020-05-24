import dhtmlparser

from lib.settings import settings

from .transformer_base import TransformerBase


class AddFaviconLinkTags(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding favicon <link> tag to all pages..")

    @classmethod
    def transform(cls, virtual_fs, root, page):
        favicon_full_url = settings.blog_url + "/favicon.ico"
        favicon_code = '<link rel="shortcut icon" href="%s">' % favicon_full_url
        favicon_tag = dhtmlparser.parseString(favicon_code)
        page.dom.find("head")[0].childs.append(favicon_tag)
