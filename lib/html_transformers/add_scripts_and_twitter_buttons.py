import dhtmlparser3

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase
from lib.preprocessors.add_static_files import AddStaticFiles


class AddScriptsAndTwitterButtons(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Twitter share button to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if page is root.outer_index or page is root.inner_index:
            return

        head = page.dom.find("head")[0]
        head[-1:] = cls._get_load_script_tag()

        body_tag = page.dom.find("body")[0]
        if page.is_embeddable:
            body_tag[-1:] = cls._get_twitter_button_tag()

        body_tag["onload"] = "on_body_load();"

    @classmethod
    def _get_load_script_tag(cls):
        return dhtmlparser3.Tag("script", parameters={"src": AddStaticFiles.js_ref})

    @classmethod
    def _get_twitter_button_tag(cls):
        twitter_button_tag = dhtmlparser3.Tag(
            "a",
            parameters={
                "class": "twitter-share-button",
                "id": "twitter_button",
                "href": "#",
            },
        )
        twitter_button_tag[0:] = dhtmlparser3.Tag(
            "img", parameters={"src": AddStaticFiles.tweet_button_ref}, is_non_pair=True
        )

        return twitter_button_tag
