import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddTwitterCards(TransformerBase):
    summary_card_html = """
     <meta name="twitter:card" content="summary" />
     <meta name="twitter:site" content="{user}" />
     <meta name="twitter:title" content="{title}" />
     <meta name="twitter:description" content="{description}" />
     """

    large_image_card_html = """
     <meta name="twitter:card" content="summary_large_image" />
     <meta name="twitter:site" content="{user}" />
     <meta name="twitter:creator" content="{user}" />
     <meta name="twitter:title" content="{title}" />
     <meta name="twitter:description" content="{description}" />
     <meta name="twitter:image" content="{image}" />
     """

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Twitter card to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        dhtmlparser.makeDoubleLinked(page.dom)
        description = page.metadata.page_description

        if not description:
            description = ""

        description = description.replace('"', "&quote;")

        if page.dom.find("img") and page.metadata.image_index != -1:
            meta_html = cls._large_image_card(description, page)
        else:
            meta_html = cls.summary_card_html.format(title=page.title,
                                                     description=description,
                                                     user=settings.twitter_handle)

        meta_tags = dhtmlparser.parseString(meta_html)

        page.dom.find("head")[0].childs.extend(meta_tags.find("meta"))

    @classmethod
    def _large_image_card(cls, description, page):
        image_index = 0
        if page.metadata.image_index >= 0:
            image_index = page.metadata.image_index

        first_image_path = page.dom.find("img")[image_index].params["src"]

        return cls.large_image_card_html.format(title=page.title,
                                                description=description,
                                                image=first_image_path,
                                                user=settings.twitter_handle)

