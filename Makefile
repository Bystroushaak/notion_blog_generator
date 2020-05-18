.PHONY: help build

.DEFAULT: build
build:
	./convert_export.py --zipfile ~/Plocha/Export*.zip \
                        --blogroot /home/bystrousak/Plocha/notion_blog_content

help:
	@echo "make"
	@echo "       Build the blog"
	@echo "make test"
	@echo "       run tests"

