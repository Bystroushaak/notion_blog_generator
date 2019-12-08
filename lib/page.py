import os
import copy
from urllib.parse import parse_qs
from urllib.parse import urlparse

import dhtmlparser
from PIL import Image

from lib import SharedResources


DEFAULT_WIDTH = 900  # 900 is the max width on the page


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
            if not a.params["href"].startswith("http"):
                a.params["href"] = "../" + a.params["href"]

        # fix also style link
        style = dom.find("link", {"rel": "stylesheet"})[0]
        style.params["href"] = "../" + style.params["href"]

        # oh, and also images
        for img in dom.find("img"):
            if not img.params["src"].startswith("http"):
                img.params["src"] = "../" + img.params["src"]

        with open(index_path, "w") as f:
            f.write(dom.prettify())

    def postprocess(self):
        self._remove_inlined_style(self.dom)
        self._add_atom_feed(self.dom)
        self._add_file_icons(self.dom)
        self._add_breadcrumb(self.dom)
        self._add_patreon_button(self.dom)
        self._add_twitter_card(self.dom)
        self._fix_notion_links(self.dom)
        self._fix_youtube_embeds(self.dom)
        self._add_analytics_tag(self.dom)
        self._generate_thumbnails(self.dom)
        self._add_favicon(self.dom)
        self._postprocess_inlined_styles(self.dom)

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
        for a in dom.find("a"):
            link_content = a.getContent().strip()
            if link_content not in self.shared.title_map:
                continue

            if not a.params.get("href", "").startswith("https://www.notion.so"):
                continue

            path = self.shared.title_map[link_content].path
            path = path.replace(" ", "%20")
            path = (path.count("/") * "../") + path

            a.params["href"] = path

    def _fix_youtube_embeds(self, dom):
        embed_code = (
            '<iframe width="100%%" height="50%%" frameborder="0" src="https://www.youtube.com/embed/%s"'
            'allow="accelerometer; autoplay; encrypted-media; gyroscope; picture-in-picture" '
            'allowfullscreen></iframe>\n\n'
        )

        youtube_links = dom.match(
            "figure",
            {"tag_name": "div", "params": {"class": "source"}},
            "a"
        )
        for link in youtube_links:
            video_url = link.params.get("href", "")
            if "youtu" not in video_url:
                continue

            if "?v=" in video_url or "&v=" in video_url:
                query = urlparse(video_url).query
                video_hash = parse_qs(query)["v"][0]

            elif "youtu.be" in video_url and "t=" in video_url and "&v=" not in video_url:
                parsed = urlparse(video_url)
                video_hash = parsed.path
                if video_hash.startswith("/"):
                    video_hash = video_hash[1:]

                if parsed.query:
                    video_hash += "?" + parsed.query.replace("t=", "start=")

            else:
                video_hash = urlparse(video_url).path[0]
                print("Unparsed alt video %s hash:%s" % (video_url, video_hash))

            html = embed_code % video_hash
            tag = dhtmlparser.parseString(html)

            link.replaceWith(tag)

    def _add_analytics_tag(self, dom):
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

    def _generate_thumbnails(self, dom):
        dhtmlparser.makeDoubleLinked(dom)

        def parse_width(tag):
            widths = [
                elem.strip().split(":")[-1].replace("%", "")
                for elem in tag.params.get("style", "").split(";")
                if elem.strip().lower().startswith("width:") and elem.strip().lower().endswith("%")
            ]

            if not widths:
                return

            return float(widths[0])

        def get_thumb_path(image_path):
            thumb_dir = os.path.dirname(image_path)
            thumb_name = os.path.basename(img.params["src"].replace("%20", " "))
            thumb_name = str(thumb_name).rsplit(".", 1)[0] + "_thumb.jpg"
            return os.path.join(thumb_dir, thumb_name)

        def create_thumbnail(abs_image_path, abs_thumb_path, width):
            img = Image.open(abs_image_path)

            if img.mode in ('RGBA', 'LA'):  # sigh..
                background = Image.new(img.mode[:-1], img.size, 'white')
                background.paste(img, img.split()[-1])
                img = background

            img.convert('RGB')

            if img.size[0] < DEFAULT_WIDTH:
                raise OSError("Already smaller than required.")

            height = img.size[1] * (img.size[0] / width)
            img.thumbnail((width, height), Image.ANTIALIAS)
            img.save(abs_thumb_path, "JPEG")
            img.close()

        def path_that_handles_percents_and_spaces():
            dirname = os.path.dirname(self.path)

            if not os.path.exists(dirname) and r"%20" in dirname:
                dirname = dirname.replace(r"%20", " ")

            return os.path.join(self.shared._blog_root, dirname)

        for img in dom.find("img"):
            if not img.params.get("src"):
                print("Warning: image without src: " % img.tagToString())
                continue

            if img.params["src"].startswith("http://") or img.params["src"].startswith("https://"):
                print("Warning: remote image: %s " % img.params["src"])
                continue

            alt_style = img.parent.parent.parent.params.get("style", "")
            if "width:" in img.params.get("style", "") and "%" in img.params.get("style", ""):
                width = parse_width(img)
                width = int(DEFAULT_WIDTH / 100.0 * width) + 5
            elif "width:" in alt_style and "%" in alt_style:
                width = parse_width(img.parent.parent.parent)
                width = int(DEFAULT_WIDTH / 100.0 * width) + 5
            else:
                width = DEFAULT_WIDTH

            rel_image_path = img.params["src"].replace(r"%20", " ")
            rel_thumb_path = get_thumb_path(rel_image_path)
            abs_image_path = os.path.join(path_that_handles_percents_and_spaces(), rel_image_path)
            abs_thumb_path = os.path.join(path_that_handles_percents_and_spaces(), rel_thumb_path)

            try:
                create_thumbnail(abs_image_path, abs_thumb_path, width)
                print("Generated thumbnail %s." % rel_thumb_path)
            except OSError as e:
                print("Can't convert %s: %s" % (abs_image_path, str(e)))
                continue

            img.params["src"] = rel_thumb_path

    def _add_favicon(self, dom):
        favicon_code = '<link rel="shortcut icon" href="http://blog.rfox.eu/favicon.ico">'
        favicon_tag = dhtmlparser.parseString(favicon_code)
        dom.find("head")[0].childs.append(favicon_tag)

    def _postprocess_inlined_styles(self, dom):
        for item in dom.find("", fn=lambda x: "style" in x.params):
            if item.getTagName() == "figure":
                item.params["style"] = item.params["style"].replace("white-space:pre-wrap;", "")
