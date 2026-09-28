import uuid
import unicodedata
from collections import defaultdict

from dhtmlparser3 import Tag

from notion_blog_generator import glyphs
from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import Directory
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import ResourceRegistry

from .postprocessor_base import PostprocessorBase
from .add_sidebars import AddSidebarsToAllPages


class AddLinkTags(PostprocessorBase):
    """
    Put a small cloth tag with the target's name glyph in front of every link
    to another page, so a page is recognizable by its glyph wherever it is
    linked. Replaces the 📂 / 📄 icons that page.icon puts into link texts.
    """

    requires = [AddSidebarsToAllPages]

    ICON_PREFIXES = ("📂 ", "📄 ")

    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Adding glyph tags to links..")

        cls._warn_about_name_collisions(root)

        registry = virtual_fs.resource_registry
        for page in root.walk_htmls():
            for link in page.dom.find("a"):
                src = cls._tag_src(link, registry, root)
                if src is None:
                    continue

                cls._strip_icon(link)
                link[0:] = Tag(
                    "img",
                    parameters={"class": "strip-mark", "alt": "", "src": src},
                    is_non_pair=True,
                )

    @classmethod
    def _tag_src(cls, link: Tag, registry: ResourceRegistry, root: Directory) -> str | None:
        href = link.parameters.get("href", "")
        pictogram = settings.url_pictograms.get(href)
        if pictogram:
            cls._strip_preceding_icon(link)
            link_uuid = str(uuid.uuid5(uuid.NAMESPACE_URL, href))
            return glyphs.tag_data_uri(link_uuid, "rust", pictogram)

        target = cls._link_target(link, registry, root)
        if target is None:
            return None

        return glyphs.tag_data_uri(target.pretty_hash, target.glyph_dye, target.pictogram)

    @classmethod
    def _link_target(
        cls, link: Tag, registry: ResourceRegistry, root: Directory
    ) -> HtmlPage | None:
        href = link.parameters.get("href", "")
        if not ResourceRegistry.is_ref_str(href):
            return None

        if "breadcrumb" in link.parameters.get("class", "").split():
            return None

        target = registry.item_by_ref_str(href)
        if target is None or not target.is_html:
            return None

        if target is root.inner_index or target is root.outer_index:
            return None

        if not glyphs.is_page_uuid(target.pretty_hash):
            return None

        return target

    @classmethod
    def _strip_icon(cls, link: Tag):
        if not link.content:
            return

        first = link.content[0]
        if isinstance(first, Tag):
            # tag pages wrap the icon as <span class="icon">📄</span>
            is_icon_span = (
                first.name == "span" and "icon" in first.parameters.get("class", "").split()
            )
            if is_icon_span:
                link.content.pop(0)
            return

        text = first.lstrip()
        for prefix in cls.ICON_PREFIXES:
            if text.startswith(prefix):
                link.content[0] = text[len(prefix) :]
                return

    @classmethod
    def _strip_preceding_icon(cls, link: Tag):
        """External links carry their emoji in the text before them: `📚 <a ..>`."""
        siblings = link.parent.content
        index = next(i for i, item in enumerate(siblings) if item is link)
        if index == 0 or not isinstance(siblings[index - 1], str):
            return

        text = siblings[index - 1].rstrip()
        if text and unicodedata.category(text[-1]) == "So":
            siblings[index - 1] = text[:-1].rstrip() + (" " if text[:-1].strip() else "")

    @classmethod
    def _warn_about_name_collisions(cls, root: Directory):
        """
        Name glyphs are a 7,381-way fingerprint, not an id; the strip under them
        still carries the full UUID, so a collision is cosmetic, not fatal.
        """
        pages_by_glyph = defaultdict(set)
        for page in root.walk_htmls():
            if glyphs.is_page_uuid(page.pretty_hash) and not page.pictogram:
                pages_by_glyph[glyphs.name_glyph(page.pretty_hash)].add(page.title)

        for titles in pages_by_glyph.values():
            if len(titles) > 1:
                settings.logger.warning("Pages share a name glyph: %s", ", ".join(sorted(titles)))
