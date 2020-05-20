#! /usr/bin/env python3
import argparse

from lib.create_abstract_tree import VirtualFS

from lib.preprocessors import get_preprocessors

from lib.postprocessors.generate_nice_filenames import empty_directory


def generate_blog(zipfile, blog_root):
    # thumb_cache = ThumbCache.create_thumb_cache(blog_root)
    empty_directory(blog_root)


    # shared_resources = SharedResources(blog_root)

    blog_tree = VirtualFS(zipfile)

    root_node = blog_tree.root
    for preprocessor in get_preprocessors():
        preprocessor.preprocess(blog_tree, root_node)

    blog_tree.store_on_disc(blog_root)

    # for zf, item in iterate_zipfile(zipfile):
    #     if item.filename.endswith(".html"):
    #         page = Page(item.filename, zf.read(item).decode("utf-8"),
    #                     shared_resources)
    #         shared_resources.add_page(item.filename, page)
    #         print(item.filename, "extracted and stored for postprocessing")
    #     else:
    #         zf.extract(item, path=blog_root)
    #         print(item.filename, "extracted")

    for filename, data in unfucked_filenames(zipfile):
        if filename.endswith(".html"):
            page = Page(filename, data, shared_resources)
            shared_resources.add_page(filename, page)
            settings.logger.info("`%s` extracted and stored for postprocessing",
                                 filename)
        else:
            _save_unpacked_data(blog_root, filename, data)
            settings.logger.info("`%s` extracted", filename)

    real_blog_root = _get_real_blog_root(blog_root)
    shared_resources._real_blog_root = real_blog_root
    shared_resources.generate_title_map()
    shared_resources.thumb_cache = thumb_cache

    postprocess_all_html_pages(shared_resources, blog_root)

    settings.logger.info("Saving all pages..")
    shared_resources.save()

    _copy_to("scripts.js", real_blog_root)
    _copy_to("tweet_button.svg", real_blog_root)
    _copy_to("icons/favicon.ico", real_blog_root)
    _copy_to("nginx_redirects.txt", real_blog_root)
    _copy_to("icons", os.path.join(real_blog_root, "icons"))  # TODO: is the second parameter really necessary?

    fix_filenames_and_generate_new_structure(blog_root, real_blog_root)


def _copy_to(copy_from, copy_to):
    if os.path.isdir(copy_from):
        shutil.copytree(os.path.join(os.path.dirname(__file__), copy_from), copy_to)
    else:
        shutil.copy(os.path.join(os.path.dirname(__file__), copy_from), copy_to)


def _save_unpacked_data(blog_root, filename, data):
    full_path = os.path.join(blog_root, filename)
    dir_path = os.path.dirname(full_path)

    os.makedirs(dir_path, exist_ok=True)

    with open(full_path, "wb") as f:
        f.write(data)


def _get_real_blog_root(blog_root):
    for path in os.listdir(blog_root):
        full_path = os.path.join(blog_root, path)
        if os.path.isdir(full_path):
            return full_path

    raise ValueError("Real blogroot not found!")


def postprocess_all_html_pages(shared_resources, blog_root):
    for path, page in shared_resources.all_pages.items():
        page.transform()

    AddSidebar.add_to_all_relevant_pages()

    for path, page in shared_resources.all_pages.items():
        page.save(blog_root)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-i",
        "--zipfile",
        help="Path to the export zipfile."
    )
    parser.add_argument(
        "-o",
        "--blogroot",
        help="Path to the blog directory / git repo."
    )

    args = parser.parse_args()

    generate_blog(args.zipfile, args.blogroot)
