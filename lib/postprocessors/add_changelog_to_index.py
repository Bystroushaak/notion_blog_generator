import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS

from lib.preprocessors.add_static_files import AddStaticFiles

from .postprocessor_base import PostprocessorBase
from lib.preprocessors.make_changelog_readable import LoadChangelogsAndMakeThemReadable


class AddMinichangelogToIndex(PostprocessorBase):
    requires = [LoadChangelogsAndMakeThemReadable]

    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Adding changelog to root index page..")

        root_index_page = root.inner_index

        content_el = root_index_page.dom.find("h1", fn=lambda x: x.getContent() == "Content")[0]

        en_changelog = root.subdir_by_name("en").changelog
        changelog = en_changelog.get_articles_as_html_for_root_index(
            settings.number_of_articles_in_minichangelog
        )

        new_content_el = dhtmlparser.parseString(changelog + content_el.__str__())
        content_el.replaceWith(new_content_el)
