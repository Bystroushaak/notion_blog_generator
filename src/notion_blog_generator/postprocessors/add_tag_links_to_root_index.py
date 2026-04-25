import dhtmlparser3

from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import Directory
from notion_blog_generator.virtual_fs import VirtualFS

from .postprocessor_base import PostprocessorBase
from .add_changelog_to_index import AddMinichangelogToIndex


class AddTagLinksToRootIndex(PostprocessorBase):
    requires = [AddMinichangelogToIndex]

    LANG_PAIRS = (
        ("en", "Tags",  "Tags"),
        ("cz", "Tagy",  "Tagy"),
    )

    TPL = ('<div style="display:contents" dir="ltr">'
           '<figure class="link-to-page">'
           '<a href="%s" title="%s"><span class="icon">🏷️</span>%s</a>'
           '</figure></div>')

    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Adding tag links to root index page..")

        page = root.inner_index
        if page is None:
            return

        registry = virtual_fs.resource_registry if virtual_fs else None

        for lang_dir, tags_dirname, label in cls.LANG_PAIRS:
            root_section = root.subdir_by_name(lang_dir, default=None)
            if root_section is None or root_section.changelog is None:
                continue

            tags_dir = root.subdir_by_name(tags_dirname, default=None)
            if tags_dir is None or tags_dir.outer_index is None:
                continue

            after_href = root_section.changelog.changelog_ref
            if registry is not None:
                new_href = registry.register_item_as_ref_str(tags_dir.outer_index)
            else:
                new_href = tags_dirname + ".html"

            cls._insert_after(page.dom, after_href, new_href, label)

    @classmethod
    def _insert_after(cls, dom, anchor_href, new_href, label):
        for fig in dom.find("figure", {"class": "link-to-page"}):
            link = fig.find("a")
            if not link or link[0]["href"] != anchor_href:
                continue

            wrapper = fig.parent
            column = wrapper.parent
            for i, child in enumerate(column.content):
                if child is wrapper:
                    new_wrap = dhtmlparser3.parse(
                        cls.TPL % (new_href, label, label)
                    ).find("div")[0]
                    column.content.insert(i + 1, new_wrap)
                    new_wrap.parent = column
                    return
