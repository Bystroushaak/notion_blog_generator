import dhtmlparser

from .postprocessor_base import Postprocessor


class AddAnalyticsTag(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        analytics_code = """
        <!-- Global site tag (gtag.js) - Google Analytics -->
        <script src="https://www.googletagmanager.com/gtag/js?id=UA-142545439-1"></script>
        <script>
          window.dataLayer = window.dataLayer || [];
          function gtag(){dataLayer.push(arguments);}
          gtag('js', new Date());
        
          gtag('config', 'UA-142545439-1');
        </script>
        """
        analytics_tag = dhtmlparser.parseString(analytics_code)
        dom.find("head")[0].childs.append(analytics_tag)
