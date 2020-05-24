import os.path

import dhtmlparser

from lib.settings import settings

from .transformer_base import TransformerBase


class AddTwitterCard(TransformerBase):
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
    def transform(cls, virtual_fs, root, page):
        dhtmlparser.makeDoubleLinked(page.dom)

        description = cls._parse_description(page)
        if not description:
            return

        if page.dom.find("img"):
            meta_html = cls._large_image_card(description, page)
        else:
            meta_html = cls.summary_card_html.format(title=page.title,
                                                     description=description,
                                                     user=settings.twitter_handle)

        meta_tags = dhtmlparser.parseString(meta_html)

        page.dom.find("head")[0].childs.extend(meta_tags.find("meta"))

    @classmethod
    def _large_image_card(cls, description, page):
        first_image_path = page.dom.find("img")[0].params["src"]

        return cls.large_image_card_html.format(title=page.title,
                                                description=description,
                                                image=first_image_path,
                                                user=settings.twitter_handle)

    @classmethod
    def _parse_description(cls, page):
        p_tags = page.dom.match(
            "body",
            {"tag_name": "div", "params": {"class": "page-body"}},
            "p"
        )

        possible_descriptions = [
            dhtmlparser.removeTags(p.getContent())
            for p in p_tags if not cls._is_unwanted_element(p)
        ]
        if possible_descriptions:
            return possible_descriptions[0]

        return ""

    @staticmethod
    def _is_unwanted_element(p):
        if p.find("time"):
            return True

        if p.params.get("class") == "column":
            return True

        if len(dhtmlparser.removeTags(p.getContent())) <= 30:
            return True

        if p.parent.params.get("class") != "page-body":
            return True

        return False
