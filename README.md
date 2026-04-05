# notion blog generator

This generates my blog from the notion.so export.

Blog url: https://blog.rfox.eu

## Installation

Requires Python 3.13+ and [uv](https://docs.astral.sh/uv/).

```bash
uv sync
```

## Usage

```bash
uv run notion-blog-generator --zipfile path/to/Export.zip --blogroot path/to/output/
```

Or use the Makefile:

```bash
make              # build with thumbnails
make no_thumbs    # build without thumbnails
make test         # run tests
```

## Project structure

```
src/notion_blog_generator/
├── main.py              # CLI entry point
├── generator.py         # BlogGenerator class
├── settings.py          # global settings
├── preprocessors/       # preprocessing pipeline (reindex, metadata, changelogs, ..)
├── html_transformers/   # per-page HTML transformations (syntax highlighting, sidebars, ..)
├── postprocessors/      # post-processing (atom feed, sitemap, ..)
└── virtual_fs/          # virtual filesystem abstraction over the Notion export
```
