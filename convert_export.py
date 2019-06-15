#! /usr/bin/env python3
import os
import shutil
import os.path
import zipfile
import argparse


class Page():
    def __init__(self, path, content):
        pass


def remove_old_blog(blog_path):
    if os.path.exists(blog_path):
        shutil.rmtree(blog_path)

    os.makedirs(blog_path, exist_ok=True)


def iterate_zipfile(zipfile_path):
    zf = zipfile.ZipFile(zipfile_path)

    for zip_info in zf.infolist():
        yield zip_info


def generate_blog(zipfile, blog_path):
    remove_old_blog(blog_path)

    for item in iterate_zipfile(zipfile):
        print(item)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "EXPORT_ZIPFILE",
        help="Path to the export zipfile."
    )

    args = parser.parse_args()

    generate_blog(args.EXPORT_ZIPFILE, "blog")