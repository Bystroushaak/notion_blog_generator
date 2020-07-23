import pytz
import tzlocal
import datetime

import pyatom
import dateparser
import dhtmlparser

from lib.settings import settings
from lib.virtual_fs import Data
from lib.virtual_fs import Directory
from lib.virtual_fs import VirtualFS

from .postprocessor_base import PostprocessorBase
from lib.preprocessors.make_changelog_readable import LoadChangelogsAndMakeThemReadable


class GenerateAtomFeedFromChangelog(PostprocessorBase):
    requires = [LoadChangelogsAndMakeThemReadable]

    @classmethod
    def postprocess(cls, virtual_fs: VirtualFS, root: Directory):
        settings.logger.info("Generating Atom feeds..")

        cls._generate_atom_feed(root, virtual_fs, root.subdir_by_name("en").changelog)
        cls._generate_atom_feed(root, virtual_fs, root.subdir_by_name("cz").changelog)

    @classmethod
    def _generate_atom_feed(cls, root, virtual_fs, changelog):
        xml = cls._generate_feed_from_last_articles(
            changelog,
            virtual_fs.resource_registry,
            settings.number_of_items_in_feed
        )
        xml_item = Data(changelog.feed_name, bytes(xml, "utf-8"))
        root.add_file(xml_item)

    @classmethod
    def _generate_feed_from_last_articles(cls, changelog, registry, how_many=10):
        # bleh
        my_timezone = pytz.timezone(str(tzlocal.get_localzone()))
        timezone = datetime.datetime.now(my_timezone).strftime('%z')

        feed = pyatom.AtomFeed(
            title=settings.blog_name,
            feed_url=changelog.atom_feed_url,
            url=settings.blog_url,
            author=settings.twitter_handle.replace("@", ""),
            timezone=timezone,
        )

        for cnt, post in enumerate(changelog.posts):
            if cnt >= how_many:
                break

            cls._add_item_to_feed(registry, feed, post)

        return feed.to_string()

    @classmethod
    def _add_item_to_feed(cls, registry, feed, post):
        title_dom = dhtmlparser.parseString(post.title)

        link = title_dom.find("a")[0]
        href = link.params.get("href", "")

        if registry.is_ref_str(href):
            item = registry.item_by_ref_str(href)

            title = item.title
            url = settings.blog_url

            path = item.path
            if not path.startswith("/") and not url.endswith("/"):
                url += "/"

            url += path
        else:
            url = href
            title = dhtmlparser.removeTags(link.getContent())

        raw_date = dhtmlparser.removeTags(post.timestamp).replace("@", "")

        feed.add(
            title=title,
            content=post.description or "No description.",
            content_type="text",
            author=settings.twitter_handle.replace("@", ""),
            url=url,
            updated=dateparser.parse(raw_date)
        )
