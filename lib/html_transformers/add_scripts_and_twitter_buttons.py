import dhtmlparser

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
        head.childs.append(cls._get_load_script_tag())

        body_tag = page.dom.find("body")[0]
        if page.is_embeddable:
            body_tag.childs.append(cls._get_twitter_button_tag())

        body_tag.params["onload"] = "on_body_load();"

    @classmethod
    def _get_load_script_tag(cls):
        load_script_code = """<script src="%s"></script>""" % AddStaticFiles.js_ref
        return dhtmlparser.parseString(load_script_code)

    @classmethod
    def _get_twitter_button_tag(cls):
        twitter_button_tag = (
            '<a class="twitter-share-button" id="twitter_button" href="#">'
            '<img src="%s" />'
            '</a>\n'
        )
        twitter_button_tag = twitter_button_tag % AddStaticFiles.tweet_button_ref

        return dhtmlparser.parseString(twitter_button_tag)
