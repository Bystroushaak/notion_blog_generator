#! /usr/bin/env python3
from lib.preprocessors.unfuck_filenames import _patch_filename


def test_patch_filename():
    filenames = (
        ("Bystroushaak s blog 702b4a575ecf4c2298f76a2786c46053.html",
         "Bystroushaak s blog.html"),
        ("Paperclips tr ky acd2a190121b46c4a5351f39a00e5cf1.html",
         "Paperclips tr ky.html"),
        ("Control panels alt interface 260648f08d0e4e7ea82d973a72a550e0",
         "Control panels alt interface"),
        ("Active%20widget%20in%20PyQT5%20QTextEdit%20a35a5d6bff794aa8b78d198babf0bbbc/example_window.png",
         "Active%20widget%20in%20PyQT5%20QTextEdit/example_window.png")
    )

    for fucked, unfucked in filenames:
        assert _patch_filename(fucked) == unfucked
