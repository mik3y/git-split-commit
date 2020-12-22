clean:
	rm -rf *.egg-info build/ dist/

format:
	black git_split_commit/

dist:
	python setup.py sdist bdist_wheel

test-release: dist
	twine upload -r testpypi dist/*

test-install:
	pip install \
		--index-url https://test.pypi.org/simple/ \
		--extra-index-url https://pypi.org/simple \
		git-split-commit

release: dist
	twine upload dist/*

.PHONY: clean format dist test-release test-install release
