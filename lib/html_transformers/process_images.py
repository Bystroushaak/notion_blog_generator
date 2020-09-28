import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase
from .add_twitter_cards import AddTwitterCards


class ProcessImages(TransformerBase):
    requires = [AddTwitterCards]

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

            if first_caption.getContent().strip() == "!ignore":
                figure.replaceWith(dhtmlparser.parseString(""))
                continue

            hrefs = first_caption.find("a", fn=lambda x: "href" in x.params)
            if hrefs:
                cls._add_link(figure, first_caption, hrefs)

    @classmethod
    def _add_link(cls, figure, first_caption, hrefs):
        images = figure.find("img")
        if not images:
            return

        figcontent = first_caption.getContent().strip()
        if figcontent.startswith("<a href=") and figcontent.endswith("</a>"):
            link_html = '<a href="%s"></a>' % hrefs[0].params["href"]
            link_el = dhtmlparser.parseString(link_html).find("a")[0]
            link_el.childs.append(images[0])

            figure.childs = [link_el]
