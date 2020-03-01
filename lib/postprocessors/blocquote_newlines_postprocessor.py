from .postprocessor_base import Postprocessor

import dhtmlparser

class BlockquoteNewlinePostprocessor(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        # keep newlines in <blockquote> tags
        for p in dom.find("blockquote"):
            for text in p.find(None, fn=lambda x: not x.isTag()):
                if "\n" not in text.getContent():
                    continue

                alt_content = text.getContent().replace("\n", "<br />")
                text.replaceWith(dhtmlparser.parseString(alt_content))
