import dateutil.parser
from collections import namedtuple

import dhtmlparser3
import requests

from lib.settings import settings
from lib.virtual_fs import HtmlPage
from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS

from .preprocessor_base import PreprocessorBase


# *sigh*
# *SIGH*
# FUCK ME SIDEWAYS
# So in order to fix up notion's HTML export fuckup, where they stopped including
# values to columns, if the column contains reference to notion page (yes, I
# reported the bug, they accepted it, told me they'll get back when they fix
# it, that was all MONTH ago), I have to connect to their API and interact with
# the table "database". I've tried several other approaches, this is the only
# one working
class ChangeLine(namedtuple("ChangeLine", "date, title, content, link")):
    headers = {
        "Accept": "application/json",
        "Notion-Version": "2022-02-22",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {settings.notion_api_token}",
    }

    @classmethod
    def yield_en_changelines(cls):
        url = (
            "https://api.notion.com/v1/databases/9439524048de45169fd74f5e92fb9598/query"
        )
        response = requests.request(
            "POST", url, json={"page_size": 1000}, headers=cls.headers
        )

        for result in response.json()["results"]:
            yield cls._parse_from_en_api(result)

    @classmethod
    def yield_cz_changelines(cls):
        url = (
            "https://api.notion.com/v1/databases/15edc7eaf4414fb29f553de30279484f/query"
        )
        response = requests.request(
            "POST", url, json={"page_size": 1000}, headers=cls.headers
        )

        for result in response.json()["results"]:
            yield cls._parse_from_en_api(result)

    @classmethod
    def _parse_from_en_api(cls, result_dict):
        properties = result_dict["properties"]
        date = properties["Updated"]["date"]["start"]
        title = ""
        for s in properties["Title"]["rich_text"]:
            title += s["plain_text"]

        content = ""
        for s in properties["Content"]["title"]:
            content += s["plain_text"]

        link = properties["Title"]["rich_text"][0]["href"]

        return ChangeLine(date, title.strip(), content.strip(), link)


class FixChangelogs(PreprocessorBase):
    @classmethod
    def preprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Fixing fucked up changelog tables..")

        changelog_titles = {"Changelog", "Změny"}
        for page in root.walk_htmls():
            if not page.is_html:
                continue

            if page.title not in changelog_titles:
                continue

            # if not cls._is_changelog_still_fucked_up(page):
            #     return

            cls._fix_fix_changelog(virtual_fs, page)

    @classmethod
    def _is_changelog_still_fucked_up(cls, changelog: HtmlPage):
        for tr_tag in changelog.dom.match("table", "tr"):
            td_tags = tr_tag.find("td")

            if len(td_tags) < 3:
                continue

            title = td_tags[1].content_str()
            if title.strip():
                return False
            else:
                return True

        raise ValueError("Weird changelog structure!")

    @classmethod
    def _fix_fix_changelog(cls, virtual_fs: VirtualFS, changelog: HtmlPage):
        if changelog.title == "Changelog":
            changelines = ChangeLine.yield_en_changelines()
        else:
            changelines = ChangeLine.yield_cz_changelines()

        changelines = sorted(changelines, key=lambda x: x.date)

        for changeline in changelines:
            settings.logger.info(changeline)

        for tr_tag in changelog.dom.match("table", "tr"):
            td_tags = tr_tag.find("td")

            if len(td_tags) < 3:
                continue

            updated = td_tags[0]
            title = td_tags[1]
            content = td_tags[2]

            changeline = changelines.pop(0)

            date_str = cls._iso_date_to_notion_date(changeline.date)
            updated.content = [dhtmlparser3.Tag("time", content=[date_str])]

            link = cls._handle_link_conversion(
                virtual_fs.resource_registry, changeline.link
            )
            linked_title = dhtmlparser3.Tag(
                "a", parameters={"href": link}, content=[changeline.title]
            )
            title.content = [linked_title]

            linked_content = dhtmlparser3.Tag(
                "a", parameters={"href": link}, content=[changeline.content]
            )
            content.content = [linked_content]

    @classmethod
    def _iso_date_to_notion_date(cls, iso_date):
        date = dateutil.parser.isoparse(iso_date)
        return date.strftime("@%Y/%m/%d %H:%M")

    @classmethod
    def _handle_link_conversion(cls, resource_registry, link: str) -> str:
        if not link.startswith("https://www.notion.so/"):
            return link

        notion_hash = link.rsplit("/", 1)[-1]
        return resource_registry.as_ref_str(resource_registry.id_by_hash(notion_hash))
