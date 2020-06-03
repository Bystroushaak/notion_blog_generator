import dhtmlparser

from lib.settings import settings

from .postprocessor_base import PostprocessorBase
from .make_changelog_readable import MakeChangelogReadable


class AddSidebarsToAllPages(PostprocessorBase):
    @classmethod
    def postprocess(cls, virtual_fs, root):
        settings.logger.info("Adding sidebars to all pages..")

        sidebar_content = MakeChangelogReadable.get_last_n_for_sidebars(
            settings.number_of_articles_in_sidebar
        )

        for page in root.walk_htmls():
            if not page.is_embeddable:
                continue

            if page is root.outer_index or page is root.inner_index:
                continue

            cls._add_sidebar_to_page(page, sidebar_content)

    @classmethod
    def _add_sidebar_to_page(cls, page, sidebar_content):
        top_tag_code = '<div id="sidebar_top">\n%s\n</div>' % sidebar_content
        bottom_tag_code = '<div id="sidebar_bottom">\n%s\n</div>' % sidebar_content

        top_tag = dhtmlparser.parseString(top_tag_code).find("div")[0]
        bottom_tag = dhtmlparser.parseString(bottom_tag_code).find("div")[0]

        body_tag = page.dom.find("body")[0]
        body_tag.childs.insert(0, top_tag)
        body_tag.childs.append(bottom_tag)
