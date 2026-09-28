from notion_blog_generator.virtual_fs import HtmlPage
from notion_blog_generator.virtual_fs import Directory
from notion_blog_generator.preprocessors.remove_dull_notion_table_files import (
    RemoveDullNotionTableFiles,
)

EMPTY_ROW = (
    '<html><body><article><header></header><div class="page-body"></div></article></body></html>'
)
REAL_PAGE = '<html><body><article><div class="page-body"><p>text</p></div></article></body></html>'


def test_all_consecutive_empty_rows_are_removed():
    root = Directory("/")
    table = Directory("Component table")
    root.add_subdir(table)
    table.set_parent(root)
    for i in range(8):
        table.add_file(HtmlPage(EMPTY_ROW, f"row {i}.html"))
    table.add_file(HtmlPage(REAL_PAGE, "real.html"))

    RemoveDullNotionTableFiles.preprocess(None, root)

    assert [f.filename for f in table.files] == ["real.html"]


def test_directory_left_empty_is_removed():
    root = Directory("/")
    article = Directory("Article")
    root.add_subdir(article)
    article.set_parent(root)
    article.add_file(HtmlPage(REAL_PAGE, "index.html"))
    table = Directory("Component table")
    article.add_subdir(table)
    table.set_parent(article)
    table.add_file(HtmlPage(EMPTY_ROW, "row.html"))

    RemoveDullNotionTableFiles.preprocess(None, root)

    assert article.subdirs == []
    assert [f.filename for f in article.files] == ["index.html"]
