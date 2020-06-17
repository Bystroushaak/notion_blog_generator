import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddAnalyticsTags(TransformerBase):
    analytics_code = """
    <!-- Global site tag (gtag.js) - Google Analytics -->
    <script src="https://www.googletagmanager.com/gtag/js?id=%s"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
    
      gtag('config', '%s');
    </script>
	<script>var ezoicId = 198743;</script>
	<script type="text/javascript" src="//go.ezoic.net/ezoic/ezoic.js"></script>
    """ % (settings.google_analytics_code, settings.google_analytics_code)
    analytics_tag = dhtmlparser.parseString(analytics_code)

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Google analytics tag to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        if settings.google_analytics_code:
            page.dom.find("head")[0].childs.append(cls.analytics_tag)
