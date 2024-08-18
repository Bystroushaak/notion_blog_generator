.PHONY: help build test no_thumbs

.DEFAULT: build
build:
	. venv/bin/activate; ./convert_export.py --zipfile ${HOME}/Plocha/*Export*.zip \
                        --blogroot ${HOME}/Plocha/xlit/notion_blog_content


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
	python3 -m pytest

no_thumbs:
	. venv/bin/activate; ./convert_export.py --zipfile ${HOME}/Plocha/Export*.zip \
                        --blogroot ${HOME}/Plocha/xlit/notion_blog_content \
                        --no-thumbs
