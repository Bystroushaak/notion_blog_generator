import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS

from .transformer_base import TransformerBase
from .add_sidebars import AddSidebarsToAllPages

from lib.preprocessors.make_changelog_readable import MakeChangelogReadable


class AddLastFiveArticlesToSidebars(TransformerBase):
    requires = [MakeChangelogReadable, AddSidebarsToAllPages]

    initialized = False
    sidebar_content = None

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding last five articles to sidebars of all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not cls.initialized:
            cls._initialize()

        if not page.is_embeddable:
            return

        cls._add_last_five_to_page(page, cls.sidebar_content)

    @classmethod
    def _initialize(cls):
        cls.sidebar_content = MakeChangelogReadable.get_last_n_for_sidebars(
            settings.number_of_articles_in_sidebar
        )

        cls.initialized = True

    @classmethod
    def _add_last_five_to_page(cls, page, sidebar_content):
        top_tag_code = '<div id="last_five_top">\n%s\n</div>' % sidebar_content
        top_tag = dhtmlparser.parseString(top_tag_code).find("div")[0]
        top_div = page.dom.find("div", {"id": "sidebar_top"})[0]
        top_div.childs.append(top_tag)

        bottom_tag_code = '<div id="last_five_bottom">\n%s\n</div>' % sidebar_content
        bottom_tag = dhtmlparser.parseString(bottom_tag_code).find("div")[0]
        bottom_div = page.dom.find("div", {"id": "sidebar_bottom"})[0]
        bottom_div.childs.append(bottom_tag)
