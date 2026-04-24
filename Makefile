.PHONY: help build test no_thumbs

.DEFAULT: build
build:
	uv run notion-blog-generator --zipfile ${HOME}/Desktop/*Export*.zip \
                                 --blogroot ${HOME}/Desktop/xlit/notion_blog_content


help:
	@echo "make"
	@echo "       Build the blog."
	@echo
	@echo "make test"
	@echo "       Run tests."
	@echo
	@echo "make no_thumbs"
	@echo "       Build the blog without thumbnails."
	@echo

test:
	uv run python3 -m pytest

no_thumbs:
	uv run notion-blog-generator --zipfile ${HOME}/Plocha/Export*.zip \
                                 --blogroot ${HOME}/Plocha/xlit/notion_blog_content \
                                 --no-thumbs
