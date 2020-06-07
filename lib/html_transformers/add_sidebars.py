import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS

from .transformer_base import TransformerBase

from lib.preprocessors.make_changelog_readable import MakeChangelogReadable


class AddSidebarsToAllPages(TransformerBase):
    requires = [MakeChangelogReadable]

    initialized = False
    sidebar_content = None

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding sidebars to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not cls.initialized:
            cls._initialize()

        if not page.is_embeddable:
            return

        if page is root.outer_index or page is root.inner_index:
            return

        cls._add_sidebar_to_page(page, cls.sidebar_content)

    @classmethod
    def _initialize(cls):
        cls.sidebar_content = MakeChangelogReadable.get_last_n_for_sidebars(
            settings.number_of_articles_in_sidebar
        )

        cls.initialized = True

    @classmethod
    def _add_sidebar_to_page(cls, page, sidebar_content):
        top_tag_code = '<div id="sidebar_top">\n%s\n</div>' % sidebar_content
        bottom_tag_code = '<div id="sidebar_bottom">\n%s\n</div>' % sidebar_content

        top_tag = dhtmlparser.parseString(top_tag_code).find("div")[0]
        bottom_tag = dhtmlparser.parseString(bottom_tag_code).find("div")[0]

        body_tag = page.dom.find("body")[0]
        body_tag.childs.insert(0, top_tag)
        body_tag.childs.append(bottom_tag)
