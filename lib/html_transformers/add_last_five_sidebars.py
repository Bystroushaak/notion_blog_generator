from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS

from .transformer_base import TransformerBase

from lib.preprocessors.make_changelog_readable import LoadChangelogsAndMakeThemReadable


class AddLastFiveArticlesToSidebars(TransformerBase):
    requires = [LoadChangelogsAndMakeThemReadable]

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding last five articles to sidebars of all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if not page.is_embeddable:
            return

        sidebar_content = page.root_section.changelog.get_last_n_for_sidebars(
            settings.number_of_articles_in_sidebar
        )

        page.sidebar.last_five_html = sidebar_content
