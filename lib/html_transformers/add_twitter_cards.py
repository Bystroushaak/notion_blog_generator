import dhtmlparser3

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddTwitterCards(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Twitter card to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        description = page.metadata.page_description

        if not description:
            description = ""

        image_tags = page.dom.find("img")
        head_tag = page.dom.find("head")[0]
        if image_tags and page.metadata.image_index != -1:
            cls._add_large_image_card(head_tag, image_tags, description, page)
        else:
            cls._add_summary_card(head_tag, description, page)

    @classmethod
    def _add_large_image_card(cls, head_tag, image_tags, description, page):
        image_index = 0
        if page.metadata.image_index >= 0:
            image_index = page.metadata.image_index

        first_image_path = image_tags[image_index]["src"]

        head_tag[-1:] = dhtmlparser3.Tag(
            "meta",
            {"name": "twitter:card", "content": "summary_large_image"},
            is_non_pair=True,
        )
        head_tag[-1:] = dhtmlparser3.Tag(
            "meta",
            {"name": "twitter:site", "content": settings.twitter_handle},
            is_non_pair=True,
        )
        head_tag[-1:] = dhtmlparser3.Tag(
            "meta",
            {"name": "twitter:creator", "content": settings.twitter_handle},
            is_non_pair=True,
        )
        head_tag[-1:] = dhtmlparser3.Tag(
            "meta",
            {"name": "twitter:title", "content": page.title},
            is_non_pair=True,
        )
        head_tag[-1:] = dhtmlparser3.Tag(
            "meta",
            {"name": "twitter:description", "content": description},
            is_non_pair=True,
        )
        head_tag[-1:] = dhtmlparser3.Tag(
            "meta",
            {"name": "twitter:image", "content": first_image_path},
            is_non_pair=True,
        )


    @classmethod
    def _add_summary_card(cls, head_tag, description, page):
        head_tag[-1:] = dhtmlparser3.Tag(
            "meta",
            {"name": "twitter:card", "content": "summary"},
            is_non_pair=True,
        )
        head_tag[-1:] = dhtmlparser3.Tag(
            "meta",
            {"name": "twitter:site", "content": settings.twitter_handle},
            is_non_pair=True,
        )
        head_tag[-1:] = dhtmlparser3.Tag(
            "meta",
            {"name": "twitter:title", "content": page.title},
            is_non_pair=True,
        )
        head_tag[-1:] = dhtmlparser3.Tag(
            "meta",
            {"name": "twitter:description", "content": description},
            is_non_pair=True,
        )
