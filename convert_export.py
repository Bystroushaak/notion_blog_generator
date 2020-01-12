#! /usr/bin/env python3
import os
import shutil
import os.path
import zipfile
import argparse

import dhtmlparser

from lib.shared_resources import SharedResources
from lib.page import Page
from lib.postprocessors import AddSidebar


def generate_blog(zipfile, blog_root):
    empty_directory(blog_root)

    shared_resources = SharedResources(blog_root)

    for zf, item in iterate_zipfile(zipfile):
        if item.filename.endswith(".html"):
            page = Page(item.filename, zf.read(item).decode("utf-8"),
                        shared_resources)
            shared_resources.add_page(item.filename, page)
            print(item.filename, "extracted and stored for postprocessing")
        else:
            zf.extract(item, path=blog_root)
            print(item.filename, "extracted")

    real_blog_root = _get_real_blog_root(blog_root)
    shared_resources._real_blog_root = real_blog_root
    shared_resources.generate_title_map()

    postprocess_all_html_pages(shared_resources, blog_root)
    shared_resources.save()

    shutil.copy(os.path.join(os.path.dirname(__file__), "favicon.ico"), real_blog_root)
    shutil.copy(os.path.join(os.path.dirname(__file__), "tweet_button.png"), real_blog_root)
    shutil.copy(os.path.join(os.path.dirname(__file__), "twitter_script.js"), real_blog_root)

    fix_filenames_and_generate_new_structure(blog_root, real_blog_root)


def _get_real_blog_root(blog_root):
    for path in os.listdir(blog_root):
        full_path = os.path.join(blog_root, path)
        if os.path.isdir(full_path):
            return full_path

    raise ValueError("Real blogroot not found!")


def empty_directory(blog_path):
    if os.path.exists(blog_path):
        shutil.rmtree(blog_path)

    os.makedirs(blog_path, exist_ok=True)


def iterate_zipfile(zipfile_path):
    zf = zipfile.ZipFile(zipfile_path)

    for zip_info in zf.infolist():
        yield zf, zip_info

    zf.close()


def postprocess_all_html_pages(shared_resources, blog_root):
    for path, page in shared_resources.all_pages.items():
        page.postprocess()

    AddSidebar.add_to_all_relevant_pages()

    for path, page in shared_resources.all_pages.items():
        page.save(blog_root)


def fix_filenames_and_generate_new_structure(blog_root, real_blog_root):
    print("Remapping old structure with spaces to new with underscore..")

    new_root = os.path.join(os.path.dirname(blog_root), "generate_nicer_url")
    empty_directory(new_root)

    # sigh..
    remapped = {}
    for root, dirs, files in os.walk(blog_root):
        for dn in dirs:
            dir_path = os.path.join(root, dn)
            alt_dir_path = _replace_spaces_and_old_blog_root(dir_path, blog_root, new_root)

            os.makedirs(alt_dir_path, exist_ok=True)
            remapped[os.path.abspath(dir_path)] = os.path.abspath(alt_dir_path)

        for fn in files:
            file_path = os.path.join(root, fn)
            alt_file_path = _replace_spaces_and_old_blog_root(file_path, blog_root, new_root)

            remapped[os.path.abspath(file_path)] = os.path.abspath(alt_file_path)
            shutil.copy(file_path, alt_file_path)

    for old_fn, new_fn in list(remapped.items()):
        if new_fn.endswith(".html") or new_fn.endswith(".htm"):
            remapped.update(_change_embed_paths_in_html(old_fn, new_fn))

    blog_subdir = os.path.basename(real_blog_root)
    blog_subdir = blog_subdir.replace(" ", "_")
    blog_subdir = blog_subdir.replace("%20", "_")
    blog_subdir_path = os.path.join(new_root, blog_subdir)

    os.rename(os.path.join(blog_subdir_path, "English_section"), os.path.join(blog_subdir_path, "en"))
    os.rename(os.path.join(blog_subdir_path, "Czech_section"), os.path.join(blog_subdir_path, "cz"))

    shutil.rmtree(blog_root)
    shutil.move(blog_subdir_path, blog_root)
    shutil.rmtree(new_root)

    _save_remappings(remapped, blog_root, os.path.join(new_root, blog_subdir))

    print("Done.")


def _replace_spaces_and_old_blog_root(old_path, blog_root, new_root):
    alt_path = old_path.replace(" ", "_")
    alt_path = alt_path.replace("%20", "_")
    return alt_path.replace(blog_root, new_root, 1)


def _change_embed_paths_in_html(orig_file_path, alt_file_path):
    with open(alt_file_path) as f:
        dom = dhtmlparser.parseString(f.read())

    orig_dirname = os.path.dirname(orig_file_path)
    new_dirname = os.path.dirname(alt_file_path)

    remapped = _fix_elements(orig_dirname, new_dirname, dom, "a", "href")
    remapped.update(_fix_elements(orig_dirname, new_dirname, dom, "img", "src"))
    remapped.update(_fix_elements(orig_dirname, new_dirname, dom, "meta", "content"))  # twitter card

    with open(alt_file_path, "w") as f:
        f.write(dom.__str__())

    return remapped


def _fix_elements(orig_dirname, new_dirname, dom, element_name, path_param):
    remapped = {}
    was_on_blog = False
    blog_domain = "http://blog.rfox.eu/"

    for tag in dom.find(element_name):
        new_path = tag.params.get(path_param)

        # mostly for twitter card
        if new_path and blog_domain in new_path:
            was_on_blog = True
            new_path = new_path.replace(blog_domain, "")

            if "Bystroushaak%20s%20blog/" in new_path:
                new_path = new_path.replace("Bystroushaak%20s%20blog/", "")

        if element_name == "meta" and tag.params.get("name") != "twitter:image":
            continue

        orig_path = new_path
        if orig_path is None or "://" in orig_path:
            continue

        new_path = _replace_spaces_and_old_blog_root(new_path, "", "")
        new_path = new_path.replace("English_section/", "en/")
        new_path = new_path.replace("Czech_section/", "cz/")

        # print("Remapping <%s %s='%s'> -> %s" % (element_name, path_param, orig_path, new_path))
        full_old_path = os.path.abspath(os.path.join(orig_dirname, orig_path))
        full_new_path = os.path.abspath(os.path.join(new_dirname, new_path))
        remapped[full_old_path] = full_new_path

        # return back the absolute URL
        if was_on_blog:
            new_path = blog_domain + new_path
        was_on_blog = False

        tag.params[path_param] = new_path


    return remapped


def _save_remappings(remapped, old_blog_root, new_root):
    old_blog_root = os.path.abspath(old_blog_root)
    new_root = os.path.abspath(new_root)

    remappings = []
    for old, new in remapped.items():
        new_sub_path = new.replace(new_root, "")

        new_sub_path = new_sub_path.replace("English_section/", "en/")
        new_sub_path = new_sub_path.replace("Czech_section/", "cz/")

        if new_sub_path == "":
            new_sub_path = "/"

        real_sub_path = new_sub_path
        if new_sub_path.startswith("/") and len(new_sub_path) > 1:
            real_sub_path = new_sub_path[1:]

        new_path = os.path.join(old_blog_root, real_sub_path)

        if not os.path.exists(new_path):
            continue

        remappings.append((old.replace(old_blog_root, ""), new_sub_path))

    nginx_redir_str = "location '%s' {\n    return 301 %s;\n}\n"
    with open("redirects_for_nginx.txt", "w") as f:
        for old, new in remappings:
            f.write(nginx_redir_str % (old, new))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "EXPORT_ZIPFILE",
        help="Path to the export zipfile."
    )

    args = parser.parse_args()

    generate_blog(args.EXPORT_ZIPFILE, "blog")
