from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import Directory
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs.resource_registry import ResourceRegistry

from .postprocessor_base import PostprocessorBase


class FixInterestingArticlesLinks(PostprocessorBase):
    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Fixing interesting articles URLs..")

        for root_file in root.files:
            if not root_file.is_html:
                continue

            if root_file.title == "Interesting articles":
                cls._fix_links(root_file)
                break

    @classmethod
    def _fix_links(cls, interesting_articles: HtmlPage):
        for a_tag in interesting_articles.dom.match("table", "td", "a"):
            a_tag["href"] = a_tag.content_str()
