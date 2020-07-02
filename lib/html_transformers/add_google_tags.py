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

    adsense_code = """<script data-ad-client="%s" src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js" async></script>"""
    adsense_tag = dhtmlparser.parseString(adsense_code % settings.google_adsense_code)

    top_vertical_ad_code = """
    <ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-8322439660353685"
     data-ad-slot="9175281399"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
"""
    top_vertical_ad_tag = dhtmlparser.parseString(top_vertical_ad_code)

    bottom_vertical_ad_code = """
    <ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-8322439660353685"
     data-ad-slot="4657737295"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>
     (adsbygoogle = window.adsbygoogle || []).push({});
</script>
"""
    bottom_vertical_ad_tag = dhtmlparser.parseString(bottom_vertical_ad_code)

    cookie_consent_code = """
<script src="https://cdn.jsdelivr.net/npm/cookieconsent@3/build/cookieconsent.min.js" data-cfasync="false"></script>
<script>
window.cookieconsent.initialise({
  "palette": {
    "popup": {
      "background": "#edeff5",
      "text": "#838391"
    },
    "button": {
      "background": "#4b81e8"
    }
  },
  "position": "bottom-left"
});
</script>
"""
    cookie_consent_tag = dhtmlparser.parseString(cookie_consent_code)

    cookie_consent_css_code = """
<script src="https://cdn.jsdelivr.net/npm/cookieconsent@3/build/cookieconsent.min.js" data-cfasync="false"></script>
<script>
window.cookieconsent.initialise({
  "palette": {
    "popup": {
      "background": "#edeff5",
      "text": "#838391"
    },
    "button": {
      "background": "#4b81e8"
    }
  },
  "position": "bottom-left"
});
</script>
"""
    cookie_consent_css_tag = dhtmlparser.parseString(cookie_consent_css_code)

    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding Google analytics & adsense tags to all pages..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        head = page.dom.find("head")[0]

        if settings.google_analytics_code:
            head.childs.append(cls.analytics_tag)

        if settings.google_adsense_code:
            head.childs.append(cls.adsense_tag)

        body = page.dom.find("body")[0]
        body.childs.insert(0, cls.top_vertical_ad_tag)
        body.childs.append(cls.bottom_vertical_ad_tag)

        body.childs.append(cls.cookie_consent_tag)
        head.childs.append(cls.cookie_consent_css_tag)
