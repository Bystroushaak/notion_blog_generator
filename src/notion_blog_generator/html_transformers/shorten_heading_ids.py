from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .transformer_base import TransformerBase


class ShortenHeadingIds(TransformerBase):
    SHORT_ID_LENGTH = 4
    HEADING_TAGS = frozenset(("h1", "h2", "h3", "h4", "h5", "h6"))
    UUID_LENGTH = 36

    heading_remap = {}

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Shortening UUID heading ids..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        page_remap = cls._shorten_in_page(page)
        cls.heading_remap.update(page_remap)
        cls._patch_intra_page_links(page, page_remap)

    @classmethod
    def _shorten_in_page(cls, page):
        page_remap = {}
        used_short_ids = set()
        for heading in page.dom.find("", fn=lambda x: x.name in cls.HEADING_TAGS):
            full_id = heading.parameters.get("id", "")
            if len(full_id) != cls.UUID_LENGTH:
                continue
            short_id = full_id[:cls.SHORT_ID_LENGTH]
            if short_id in used_short_ids:
                continue
            used_short_ids.add(short_id)
            page_remap[full_id] = short_id
            heading["id"] = short_id
        return page_remap

    @classmethod
    def _patch_intra_page_links(cls, page, page_remap):
        for a in page.dom.find("a"):
            href = a.parameters.get("href", "")
            if not href.startswith("#"):
                continue
            target = href[1:]
            if len(target) == 32 and "-" not in target:
                target = HtmlPage.normalize_block_id(target)
            if target in page_remap:
                a["href"] = "#" + page_remap[target]
