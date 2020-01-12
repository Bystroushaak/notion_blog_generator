import dhtmlparser
from prog_lang_detector.classify import classify

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


from .postprocessor_base import Postprocessor


class AddSyntaxHighlighting(Postprocessor):
    @classmethod
    def postprocess(cls, dom, page, shared):
        dhtmlparser.makeDoubleLinked(dom)

        formatter = HtmlFormatter(wrapcode=False)
        add_style_to_the_header = False
        for code in dom.match(["pre", {"class": "code"}], "code"):
            code_content = code.getContent()
            code_content = code_content.replace("&#x27;", '"')
            code_content = code_content.replace("&#x39;", "'")
            code_content = code_content.replace("&#x60;", '<')
            code_content = code_content.replace("&#x62;", '>')
            code_content = code_content.replace("&#x38;", '&')
            lang = classify(code_content, print_details=False)

            if lang == "python":
                colored_text = highlight(code_content, PythonLexer(), formatter)
                pre_tag = dhtmlparser.parseString(colored_text).find("pre")[0]

                # wrap content of the <pre> to the <code>
                code_tag = dhtmlparser.parseString("<code></code>").find("code")[0]
                code_tag.childs = pre_tag.childs
                pre_tag.childs = [code_tag]
                pre_tag.params["class"] = "code"

                code.parent.replaceWith(pre_tag)
                add_style_to_the_header = True

        if add_style_to_the_header:
            style = HtmlFormatter().get_style_defs()
            style_html = "<style>\n%s\n</style>" % style
            dom.find("head")[0].childs.append(dhtmlparser.parseString(style_html))
