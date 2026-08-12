.PHONY: clean build upload

XARGS := xargs $(shell test $$(uname) = Linux && echo -r)

clean:
	rm -rf dist
	find . -name '*.pyc' -print0 | $(XARGS) -0 rm
	find . -name '*~' -print0 | $(XARGS) -0 rm

build: clean
	uv build

# The upload target requires that you have access rights to PYPI, either
# via a configured token (see 'uv publish --help') or trusted publishing.
upload: build
	uv publish
