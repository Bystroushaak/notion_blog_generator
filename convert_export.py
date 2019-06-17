#! /usr/bin/env python3
import os
import sys
import copy
import shutil
import os.path
import zipfile
import argparse

import dhtmlparser


class SharedResources:
    def __init__(self, blog_root, all_pages):
        self.css = ""
        self._css_path = "style.css"
        self._blog_root = blog_root
        self.all_pages = all_pages
        self.title_map = None

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

.corner-ribbon.red{background: #e43;}"""

        return self._css_path

    def save(self):
        with open(os.path.join(self._blog_root, self._css_path), "w") as f:
            f.write(self.css.strip() + "\n\n")

    def generate_title_map(self):
        self.title_map = {
            page.title: page
            for page in self.all_pages.values()
        }



class Page:
    def __init__(self, path: str, content, shared: SharedResources):
        self.path = path
        self.content = content
        self.shared = shared
        self.dom = dhtmlparser.parseString(self.content)

        self.is_index = False

    @property
    def title(self):
        return self.dom.find("h1", {"class": "page-title"})[0].getContent()

    def save(self, blog_path):
        path = os.path.join(blog_path, self.path)

        dirname = os.path.dirname(path)
        if not os.path.exists(dirname):
            os.makedirs(dirname, exist_ok=True)

        with open(path, "w") as f:
            f.write(self.dom.prettify())

        if self.is_index:
            self._save_also_index_page(path)

    def _save_also_index_page(self, path):
        full_path_without_filetype = path.rsplit(".", 1)[0]
        index_path = os.path.join(full_path_without_filetype, "index.html")
        dirname = full_path_without_filetype.rsplit("/", 1)[-1]

        if not os.path.exists(full_path_without_filetype):
            os.makedirs(full_path_without_filetype, exist_ok=True)

        # fix all local links
        dom = copy.copy(self.dom)
        for a in dom.find("a"):
            if not "href" in a.params:
                continue

            # fixed later
            if a.params.get("class", "") == "breadcrumb":
                continue

            href = a.params["href"]
            if href.startswith(dirname):
                a.params["href"] = href.split("/", 1)[-1]

        # fix breadcrumb links
        for a in dom.find("a", {"class": 'breadcrumb'}):
            a.params["href"] = "../" + a.params["href"]

        # fix also style link
        style = dom.find("link", {"rel": "stylesheet"})[0]
        style.params["href"] = "../" + style.params["href"]

        with open(index_path, "w") as f:
            f.write(dom.prettify())

    def postprocess(self):
        self._remove_inlined_style(self.dom)
        # self._add_utf_declaration(self.dom)
        self._add_atom_feed(self.dom)
        self._add_file_icons(self.dom)
        self._add_breadcrumb(self.dom)
        self._add_patreon_button(self.dom)
        self._add_twitter_card(self.dom)
        self._fix_notion_links(self.dom)

        full_path_without_filetype = self.path.rsplit(".", 1)[0]
        for path in self.shared.all_pages.keys():
            if path.startswith(full_path_without_filetype + "/"):
                self.is_index = True
                break

    def _remove_inlined_style(self, dom):
        style = dom.match("head", "style")[0]

        style_path = self.shared.add_css(style.getContent())
        style_path = ("../" * self.path.count("/")) + style_path

        style_str = '<link rel="stylesheet" type="text/css" href="%s">' % style_path
        new_style = dhtmlparser.parseString(style_str).find("link")[0]

        style.replaceWith(new_style)

    def _add_utf_declaration(self, dom):
        head = dom.find("head")[0]

        utf_tag_str = '<meta http-equiv="Content-Type" content="text/html; charset=utf-8">'
        utf_tag = dhtmlparser.parseString(utf_tag_str).find("meta")[0]

        head.childs.append(utf_tag)

    def _add_atom_feed(self, dom):
        head = dom.find("head")[0]

        atom_tag_str = (
            '<link rel="alternate" type="application/atom+xml" '
            'href="http://rfox.eu/raw/feeds/notion_blog.xml" />'
        )
        atom_tag = dhtmlparser.parseString(atom_tag_str).find("link")[0]

        head.childs.append(atom_tag)

    def _add_file_icons(self, dom):
        file_icon_str = '<span class="icon">🗎</span>'
        file_icon_tag = dhtmlparser.parseString(file_icon_str).find("span")[0]

        for figure in dom.find("figure", {"class": "link-to-page"}):
            if figure.find("span", {"class": "icon"}):
                continue

            a = figure.find("a")
            if not a:
                continue

            a[0].childs.insert(0, file_icon_tag)

    def _add_breadcrumb(self, dom):
        if "/" not in self.path:
            return

        bread_crumbs = []

        path = ""
        dirs = self.path.rsplit("/", 1)[0].split("/")  # just the dirs
        for dirname in dirs:
            full_path = os.path.join(path, dirname + ".html")
            title = self.shared.all_pages[full_path].title
            path_up = (len(dirs) - len(full_path.split("/"))) * "../" + "index.html"
            bread_crumbs.append([path_up, title])
            path = os.path.join(path, dirname)

        items = ["<a href='{}' class='breadcrumb'>{}</a>".format(*item)
                 for item in bread_crumbs]
        items.append(self.title)

        all_items = " / ".join(items) + "\n\n"
        all_items_tag = dhtmlparser.parseString(all_items)

        dom.find("body")[0].childs.insert(0, all_items_tag)

    def _add_patreon_button(self, dom):
        html_code = (
            '<div class="corner-ribbon top-right red">'
            '<a href="https://www.patreon.com/bePatron?u=2618881">Become a Patron</a>'
            '</div>'
        )
        button_tag = dhtmlparser.parseString(html_code)

        dom.find("body")[0].childs.append(button_tag)

    def _add_twitter_card(self, dom):
        summary_card = """
        <meta name="twitter:card" content="summary" />
        <meta name="twitter:site" content="@Bystroushaak" />
        <meta name="twitter:title" content="{title}" />
        <meta name="twitter:description" content="{description}" />
        """

        large_image_card_html = """
        <meta name="twitter:card" content="summary_large_image" />
        <meta name="twitter:site" content="@Bystroushaak" />
        <meta name="twitter:creator" content="@Bystroushaak" />
        <meta name="twitter:title" content="{title}" />
        <meta name="twitter:description" content="{description}" />
        <meta name="twitter:image" content="http://blog.rfox.eu/{image}" />
        """

        dhtmlparser.makeDoubleLinked(dom)

        p_tags = dom.match(
            "body",
            {"tag_name": "div", "params": {"class": "page-body"}},
            "p"
        )
        possible_descriptions = [
            dhtmlparser.removeTags(p.getContent()) for p in p_tags
            if not p.find("time") and p.params.get("class") != "column" and \
            len(dhtmlparser.removeTags(p.getContent())) > 30 and p.parent.params.get("class") == "page-body"
        ]
        description = ""
        if possible_descriptions:
            description = possible_descriptions[0]

        if not description:
            return

        if dom.find("img"):
            first_image_path = dom.find("img")[0].params["src"]
            full_img_path = os.path.join(os.path.dirname(self.path), first_image_path)

            meta_html = large_image_card_html.format(
                title=self.title,
                description=description,
                image=full_img_path.replace(" ", "%20")
            )
        else:
            meta_html = summary_card.format(
                title=self.title,
                description=description,
            )

        meta_tags = dhtmlparser.parseString(meta_html)

        dom.find("head")[0].childs.extend(meta_tags.find("meta"))

    def _fix_notion_links(self, dom):
        links = dom.find("a", fn=lambda x: x.params.get("href", "").startswith("https://www.notion.so"))
        for a in links:
            link_content = a.getContent().strip()
            if link_content not in self.shared.title_map:
                continue

            path = self.shared.title_map[link_content].path
            path = path.replace(" ", "%20")
            path = (path.count("/") * "../") + path
            a.params["href"] = path


def generate_blog(zipfile, blog_root):
    remove_old_blog(blog_root)

    all_pages = {}
    shared_resources = SharedResources(blog_root, all_pages)

    for zf, item in iterate_zipfile(zipfile):
        if item.filename.endswith(".html"):
            all_pages[item.filename] = Page(item.filename,
                                            zf.read(item).decode("utf-8"),
                                            shared_resources)
            print(item.filename, "extracted and stored for postprocessing")
        else:
            zf.extract(item, path=blog_root)
            print(item.filename, "extracted")

    shared_resources.generate_title_map()

    postprocess_html(all_pages, blog_root)
    shared_resources.save()


def remove_old_blog(blog_path):
    if os.path.exists(blog_path):
        shutil.rmtree(blog_path)

    os.makedirs(blog_path, exist_ok=True)


def iterate_zipfile(zipfile_path):
    zf = zipfile.ZipFile(zipfile_path)

    for zip_info in zf.infolist():
        yield zf, zip_info

    zf.close()


def postprocess_html(all_pages, blog_path):
    for path, page in all_pages.items():
        page.postprocess()
        page.save(blog_path)

    find_and_rename_index_page(all_pages, blog_path)

def find_and_rename_index_page(all_pages, blog_path):
    root_pages = [root_page for root_page in all_pages.values()
                  if not os.path.dirname(root_page.path)]

    if len(root_pages) != 1:
        raise ValueError("Fuck, multiple root pages, implement --root-page switch later.")

    root_page = root_pages[0]

    os.rename(os.path.join(blog_path, root_page.path),
              os.path.join(blog_path, "index.html"))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "EXPORT_ZIPFILE",
        help="Path to the export zipfile."
    )

    args = parser.parse_args()

    generate_blog(args.EXPORT_ZIPFILE, "blog")
