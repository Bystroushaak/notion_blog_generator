from typing import Iterator

from notion_blog_generator.settings import settings

from notional import connect
from notional.text import CodingLanguage
from notional.blocks import Code
from notional.blocks import Page
from notional.blocks import Block
from notional.blocks import ChildPage


notion = connect(auth=settings.notion_api_token)


def walk_page_tree(page: Page):
    yield page

    for child_page in filter_blocks(page, lambda x: isinstance(x, ChildPage)):
        yield from walk_page_tree(notion.pages.retrieve(child_page.id))


def filter_blocks(page, filter) -> Iterator[Block]:
    for block in walk_blocks(page):
        if filter(block):
            yield block


def walk_blocks(page: Page | Block) -> Iterator[Block]:
    for block in notion.blocks.children.list(page):
        yield block

        if isinstance(block, ChildPage):
            continue

        if block.has_children:
            yield from walk_blocks(block)


def is_meta_code_block(block: Block) -> bool:
    if not isinstance(block, Code):
        return False

    # if block.code.language != CodingLanguage.YAML:
    #     return False

    content = block.PlainText
    if content.strip().lower().splitlines()[0] != "#lang:metadata":
        return False

    return True
