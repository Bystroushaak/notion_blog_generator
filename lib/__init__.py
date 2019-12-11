import os


class SharedResources:
    def __init__(self, blog_root):
        self.css = ""
        self._css_path = "style.css"
        self._blog_root = blog_root
        self.all_pages = {}
        self.title_map = None

        # sigh, notion uses index page as sort of fake root, this is the real one
        self._real_blog_root = None

    def add_css(self, css):
        self.css = css

        self.css += """
.corner-ribbon{
  width: 14em;
  background: #e43;
  position: absolute;
  text-align: center;
  line-height: 2.5em;
  letter-spacing: 1px;
  color: #f0f0f0;
  transform: rotate(-45deg);
  -webkit-transform: rotate(-45deg);
  position: fixed;
  box-shadow: 0 0 3px rgba(0,0,0,.3);
}

.corner-ribbon.top-right{
  top: 2.8em;
  right: -3em;
  left: auto;
  transform: rotate(45deg);
  -webkit-transform: rotate(45deg);
}

.corner-ribbon.bottom-right{
  top: auto;
  right: -50px;
  bottom: 25px;
  left: auto;
  transform: rotate(-45deg);
  -webkit-transform: rotate(-45deg);
}

.corner-ribbon.red{background: #e43;}

pre {
 white-space: pre-wrap;       /* css-3 */
 white-space: -moz-pre-wrap;  /* Mozilla, since 1999 */
 white-space: -pre-wrap;      /* Opera 4-6 */
 white-space: -o-pre-wrap;    /* Opera 7 */
 word-wrap: break-word;       /* Internet Explorer 5.5+ */
}

figure iframe {
    height: 550px;
}
"""

        return self._css_path

    def add_page(self, filename, page):
        """
        Args:
            filename (str):
            page (Page):
        """
        self.all_pages[filename] = page

    def save(self):
        self.css = self.css.replace("white-space: pre-wrap;\n", "", 1)
        with open(os.path.join(self._real_blog_root, self._css_path), "w") as f:
            f.write(self.css.strip() + "\n\n")

    def generate_title_map(self):
        self.title_map = {
            page.title: page
            for page in self.all_pages.values()
        }