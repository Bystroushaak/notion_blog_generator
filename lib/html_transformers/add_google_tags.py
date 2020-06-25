import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddGoogleTags(TransformerBase):
    analytics_code = """
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
    
      gtag('config', '%s');
    </script>
    """ % (settings.google_analytics_code, settings.google_analytics_code)
    analytics_tag = dhtmlparser.parseString(analytics_code)

    adsense_code = """<script data-ad-client="%s" async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js"></script>"""
    adsense_tag = dhtmlparser.parseString(adsense_code % settings.google_adsense_code)

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Google analytics & adsense tags to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if settings.google_analytics_code:
            page.dom.find("head")[0].childs.append(cls.analytics_tag)

        if settings.google_adsense_code:
            page.dom.find("head")[0].childs.append(cls.adsense_tag)
