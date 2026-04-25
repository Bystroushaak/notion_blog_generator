import dhtmlparser3

from notion_blog_generator.settings import settings
from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import VirtualFS
from notion_blog_generator.virtual_fs import Directory

from .transformer_base import TransformerBase
from .add_social_cards import AddSocialCards


class ProcessImages(TransformerBase):
    requires = [AddSocialCards]

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Processing images (adding link, removing ignored) ..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        for figure in page.dom.find("figure"):
            figcaptions = figure.find('figcaption')
            if not figcaptions:
                continue

            first_caption = figcaptions[0]

            if first_caption.content_str().strip() == "!ignore":
                figure.replace_with(dhtmlparser3.Tag(""))
                continue

            hrefs = first_caption.find("a", fn=lambda x: "href" in x)
            if hrefs:
                cls._add_link(figure, first_caption, hrefs)

    @classmethod
    def _add_link(cls, figure, first_caption, hrefs):
        images = figure.find("img")
        if not images:
            return

        figcontent = first_caption.content_str().strip()
        if figcontent.startswith("<a href=") and figcontent.endswith("</a>"):
            link_el = dhtmlparser3.Tag("a", {"href": hrefs[0]["href"]})
            link_el[-1:] = images[0]

            figure.content = []
            figure[0:] = link_el
