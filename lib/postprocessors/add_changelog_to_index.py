import dhtmlparser

from lib.settings import settings
from lib.html_transformers import MakeChangelogReadable
from lib.preprocessors.add_static_files import AddStaticFiles

from .postprocessor_base import PostprocessorBase


class AddChangelogToIndex(PostprocessorBase):
    @classmethod
    def postprocess(cls, virtual_fs, root):
        settings.logger.info("Adding changelog to root index page..")

        root_index_page = root.inner_index

        if not MakeChangelogReadable.is_set:
            raise ValueError(
                "MakeChangelogReadable is empty, can't generate minichangelog!"
            )

        content_id = "93217684-c41c-49f8-88b4-347410b2c330"
        content_el = root_index_page.dom.find("h1", {"id": content_id})[0]
        changelog = MakeChangelogReadable.get_articles_as_html_for_root_index(
            settings.number_of_articles_in_minichangelog
        )

        mew_content_el = dhtmlparser.parseString(changelog + content_el.__str__())
        content_el.replaceWith(mew_content_el)

        cls._insert_twitter_and_rss_buttons(root_index_page.dom)

    @classmethod
    def _insert_twitter_and_rss_buttons(cls, dom):
        paragraph_id = "bd75b1ce-a053-435a-bad4-df9a25c87e6f"
        feed_mention_paragraph = dom.find("p", {"id": paragraph_id})[0]

        div_html = """
        <div align="center">
            <a href="{rss_feed_url}"><img src="{rss_icon_url}" style="width: 4em;" /></a>
            &nbsp; &nbsp;
            <a href="{twitter_url}"><img src="{twitter_icon_url}" style="width: 4em;" /></a>
        </div>
        """
        div_html = div_html.format(rss_feed_url=settings.atom_feed_url,
                                   rss_icon_url=AddStaticFiles.rss_icon_ref,
                                   twitter_url=settings.twitter_url,
                                   twitter_icon_url=AddStaticFiles.twitter_icon_ref)

        feed_mention_paragraph.childs.append(dhtmlparser.parseString(div_html))
