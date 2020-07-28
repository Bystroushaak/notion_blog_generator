import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddImageLinks(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Converting images with link captions to linked images..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        for figure in page.dom.find("figure"):
            figcaptions = figure.find('figcaption')
            if not figcaptions:
                continue

            hrefs = figcaptions[0].find("a", fn=lambda x: "href" in x.params)
            if not hrefs:
                continue

            images = figure.find("img")
            if not images:
                continue

            figcontent = figcaptions[0].getContent().strip()
            if figcontent.startswith("<a href=") and figcontent.endswith("</a>"):
                link_html = '<a href="%s"></a>' % hrefs[0].params["href"]
                link_el = dhtmlparser.parseString(link_html).find("a")[0]
                link_el.childs.append(images[0])

                figure.childs = [link_el]
