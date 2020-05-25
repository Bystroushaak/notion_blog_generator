.PHONY: help build test

.DEFAULT: build
build:
	./convert_export.py --zipfile ~/Plocha/Export*.zip \
                        --blogroot /home/bystrousak/Plocha/xlit/notion_blog_content

help:
	@echo "make"
	@echo "       Build the blog."
	@echo "make test"
	@echo "       Run tests."

test:
	python3 -m pytest
