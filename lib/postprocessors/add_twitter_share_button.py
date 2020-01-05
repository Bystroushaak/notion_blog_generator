import os.path

import dhtmlparser

from .postprocessor_base import Postprocessor


class AddTwitterShareButton(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        twitter_load_script = """
<script>window.twttr = (function(d, s, id) {
  var js, fjs = d.getElementsByTagName(s)[0],
    t = window.twttr || {};
  if (d.getElementById(id)) return t;
  js = d.createElement(s);
  js.id = id;
  js.src = "https://platform.twitter.com/widgets.js";
  fjs.parentNode.insertBefore(js, fjs);

  t._e = [];
  t.ready = function(f) {
    t._e.push(f);
  };

  return t;
}(document, "script", "twitter-wjs"));</script>
        """

        twitter_share_button = """
<a class="twitter-share-button"
   href="https://twitter.com/intent/tweet?via=Bystroushaak">Tweet</a>
        """

        head = dom.find("head")[0]
        head.childs.append(dhtmlparser.parseString(twitter_load_script))

        body_tag = dom.find("body")[0]
        body_tag.childs.append(dhtmlparser.parseString(twitter_share_button))
