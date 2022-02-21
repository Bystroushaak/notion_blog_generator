from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class MakeNotionLinksLocal(TransformerBase):
    initliazed = False
    title_to_ref_map = {}
    title_to_item_map = {}
    hash_to_ref_map = {}

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Converting stalled notion.so links to local paths..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not cls.initliazed:
            cls.initialize(virtual_fs.resource_registry, root)

        for a in page.dom.find("a"):
            link_content = a.content_str().strip()
            original_href = a.parameters.get("href", "")
            if not original_href.startswith("https://www.notion.so"):
                continue

            # skip referral links
            if original_href.startswith("https://www.notion.so/?r="):
                continue

            path = page.path
            if path.startswith("/Changelog/") or path.startswith("/Changelog.html"):
                continue

            hash = cls._hash_from_link(original_href)
            if hash in cls.hash_to_ref_map:
                ref_str = cls.hash_to_ref_map[hash]
                a["href"] = ref_str
                continue

            if link_content in cls.title_to_ref_map:
                ref_str = cls.title_to_ref_map[link_content]
                a["href"] = ref_str
                continue

            settings.logger.error("Couldn't patch %s in %s.", original_href,
                                  page.path)


    @classmethod
    def initialize(cls, resource_registry, root):
        for page in root.walk_htmls():
            ref_str = resource_registry.register_item_as_ref_str(page)
            item_title = page.title

            cls.title_to_ref_map[item_title] = ref_str
            cls.title_to_item_map[item_title] = page
            cls.hash_to_ref_map[page.hash] = ref_str

        cls.initliazed = True

    @classmethod
    def _hash_from_link(cls, original_href):
        return original_href.split("-")[-1].split("#")[0]
