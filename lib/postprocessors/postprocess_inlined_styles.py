from .postprocessor_base import Postprocessor


class PostprocessInlinedStyles(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        for item in dom.find("", fn=lambda x: "style" in x.params):
            if item.getTagName() == "figure":
                item.params["style"] = item.params["style"].replace("white-space:pre-wrap;", "")
