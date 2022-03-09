import html

import dhtmlparser3
# from prog_lang_detector.classify import classify

from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers.c_cpp import CLexer
from pygments.lexers.c_cpp import CppLexer
from pygments.lexers.jvm import JavaLexer
from pygments.lexers.css import CssLexer
from pygments.lexers.data import YamlLexer
from pygments.lexers.html import XmlLexer
from pygments.lexers.html import HtmlLexer
from pygments.lexers.python import PythonLexer
from pygments.lexers.smalltalk import SmalltalkLexer


from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import VirtualFS
from lib.virtual_fs import Directory

from .transformer_base import TransformerBase


class AddSyntaxHighlighting(TransformerBase):
    @classmethod
    def log_transformer(cls):
        settings.logger.info("Adding syntax highlighting to <pre> elements..")

    @classmethod
    def transform(cls, virtual_fs: VirtualFS, root: Directory, page: HtmlPage):
        add_style_to_the_header = False

        code_code = page.dom.match(["pre", {"class": "code"}], "code")
        code_wrap = page.dom.match(["pre", {"class": "code code-wrap"}], "code")
        for code_tag in code_code + code_wrap:
            code_content, lang = cls._parse_code_content_and_lang(code_tag)

            add_style_to_the_header = True
            if lang == "python" or lang == "python3" or lang == "py":
                cls._add_syntax_highlight_for(PythonLexer, code_tag, code_content)
            elif lang == "c":
                cls._add_syntax_highlight_for(CLexer, code_tag, code_content)
            elif lang == "c++" or lang == "cpp":
                cls._add_syntax_highlight_for(CppLexer, code_tag, code_content)
            elif lang == "java":
                cls._add_syntax_highlight_for(JavaLexer, code_tag, code_content)
            elif lang == "smalltalk":
                cls._add_syntax_highlight_for(SmalltalkLexer, code_tag, code_content)
            elif lang == "xml":
                cls._add_syntax_highlight_for(XmlLexer, code_tag, code_content)
            elif lang == "html":
                cls._add_syntax_highlight_for(HtmlLexer, code_tag, code_content)
            elif lang == "css":
                cls._add_syntax_highlight_for(CssLexer, code_tag, code_content)
            elif lang == "yaml":
                cls._add_syntax_highlight_for(YamlLexer, code_tag, code_content)
            elif lang:
                settings.logger.error("Unknown lang definition: %s, skipping.", lang)
                add_style_to_the_header = False
            else:
                add_style_to_the_header = False

        if add_style_to_the_header:
            style = HtmlFormatter().get_style_defs()
            style_tag = dhtmlparser3.Tag("style", content=["\n", style, "\n"])
            page.dom.find("head")[0][-1:] = style_tag

    @classmethod
    def _add_syntax_highlight_for(cls, lexer, code, code_content):
        formatter = HtmlFormatter(wrapcode=False)

        colored_text = highlight(code_content, lexer(), formatter)
        pre_tag = dhtmlparser3.parse(colored_text).find("pre")[0]

        # wrap content of the <pre> to the <code>
        code_tag = dhtmlparser3.Tag("code")
        code_tag.content = pre_tag.content
        pre_tag.content = [code_tag]
        pre_tag["class"] = "code"

        pre_tag.double_link()
        code.parent.replace_with(pre_tag)

    @classmethod
    def _parse_code_content_and_lang(cls, code):
        code_content = html.unescape(code.content_str())
        code_content_lines = code_content.splitlines()

        lang = ""
        if "lang:" in code_content_lines[0]:
            lang = code_content_lines[0].split("lang:", 1)[-1].strip()
            code_content = "\n".join(code_content_lines[1:])
        # elif settings.lang_classificator_enabled:
        #     lang = classify(code_content, print_details=False)

        return code_content, lang
