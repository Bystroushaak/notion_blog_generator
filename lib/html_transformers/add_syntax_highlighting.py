import html

import dhtmlparser
from prog_lang_detector.classify import classify

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


from lib.settings import settings

from .transformer_base import TransformerBase


class AddSyntaxHighlighting(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding syntax highlighting to <pre> elements..")

    @classmethod
    def transform(cls, virtual_fs, root, page):
        dhtmlparser.makeDoubleLinked(page.dom)


        add_style_to_the_header = False
        for code_tag in page.dom.match(["pre", {"class": "code"}], "code"):
            code_content, lang = cls._parse_code_content_and_lang(code_tag)

            if lang == "python" or lang == "python3":
                cls._add_syntax_highlight_for_python(code_tag, code_content)
                add_style_to_the_header = True

        if add_style_to_the_header:
            style = HtmlFormatter().get_style_defs()
            style_html = "<style>\n%s\n</style>" % style
            style_tag = dhtmlparser.parseString(style_html)
            page.dom.find("head")[0].childs.append(style_tag)

    @classmethod
    def _add_syntax_highlight_for_python(cls, code, code_content):
        formatter = HtmlFormatter(wrapcode=False)

        colored_text = highlight(code_content, PythonLexer(), formatter)
        pre_tag = dhtmlparser.parseString(colored_text).find("pre")[0]

        # wrap content of the <pre> to the <code>
        code_tag = dhtmlparser.parseString("<code></code>").find("code")[0]
        code_tag.childs = pre_tag.childs
        pre_tag.childs = [code_tag]
        pre_tag.params["class"] = "code"

        code.parent.replaceWith(pre_tag)

    @classmethod
    def _parse_code_content_and_lang(cls, code):
        code_content = html.unescape(code.getContent())
        code_content_lines = code_content.splitlines()

        if "lang:" in code_content_lines[0]:
            lang = code_content_lines[0].split("lang:", 1)[-1].strip()
            code_content = "\n".join(code_content_lines[1:])
        else:
            lang = classify(code_content, print_details=False)

        return code_content, lang
