"""
Sigh. Notion just out of random inserted some kind of hashes or UUID's into all
filenames, which of course fucks everything up beyond recognition.
"""
import re
import os.path
import zipfile

import dhtmlparser

from lib.settings import settings


def unfucked_filenames(zipfile):
    settings.logger.info("Unfucking filenames..")

    for zf, item in iterate_zipfile(zipfile):
        if item.filename.endswith(".html"):
            data = zf.read(item).decode("utf-8")
            yield _patch_html_filename(item.filename, data), _patch_links(data)
        else:
            data = zf.read(item)
            yield _patch_filename(item.filename), data

    settings.logger.info("Filenames unfucked.")


def iterate_zipfile(zipfile_path):
    zf = zipfile.ZipFile(zipfile_path)

    for zip_info in zf.infolist():
        yield zf, zip_info

    zf.close()


def _patch_links(data):
    dom = dhtmlparser.parseString(data)

    for a in dom.find("a"):
        if "href" not in a.params or "://" in a.params.get("href", ""):
            continue

        a.params["href"] = _patch_filename(a.params["href"])

    for img in dom.find("img"):
        if "src" not in img.params or "://" in img.params.get("src", ""):
            continue

        img.params["src"] = _patch_filename(img.params["src"])

    return dom.__str__()


def _patch_filename(filename):
    # "English section 8f6665fa0621410daa32502748e3cc5d.html"
    # -> "English section"
    return re.sub(' [a-z0-9]{32}|%20[a-z0-9]{32}', '', filename)


def _patch_html_filename(original_fn, data):
    dom = dhtmlparser.parseString(data)

    h1 = dom.find("h1")

    if not h1:
        return _patch_filename(original_fn)

    return os.path.join(os.path.dirname(original_fn),
                        _normalize_unicode(h1[0].getContent()) + ".html")


def _normalize_unicode(unicode_name):
    ascii_name = unicode_name.replace(" ", "_")

    return ascii_name
