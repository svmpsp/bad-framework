#!/usr/bin/env make

PYTHON_VERSION := 3.7.13
PACKAGE_NAME := bad_framework
VENV_NAME := $(PACKAGE_NAME)-$(PYTHON_VERSION)

SRC_DIR := bad_framework
TEST_DIR := tests
INSTALL_DIR := install

CONFIG_FILES := pyproject.toml docsrc/conf.py
SOURCES := $(shell find $(PACKAGE_NAME) -name *.py)
TEST_SOURCES := $(shell find tests -name *.py)
DOC_SOURCES := $(shell find docsrc | grep -v '.*_.*')
BUILD_SOURCES := $(CONFIG_FILES) $(SOURCES) $(TEST_SOURCES)

POETRY_CMD := poetry run

all: package docs

### - docs: builds the documentation.
docs: $(DOC_SOURCES) .python-version
	@echo ">>> Creating project documentation..."
	$(POETRY_CMD) $(MAKE) -C docsrc html
	cp -a ./docsrc/_build/html/. ./docs
	@echo "<<< Done"

format: .build_format_report
.build_format_report: $(BUILD_SOURCES)
	@echo ">>> Formatting Python code..."
	-rm -f $@
	-rm -f .coverage
	$(POETRY_CMD) black . && (echo "All is well!" > $@)
	@echo "<<< Done."
	

### - test: runs unit and integration tests.
test: .build_pytest_report
.build_pytest_report: $(BUILD_SOURCES) .build_format_report
	@echo ">>> Running tests..."
	-rm -f $@
	-rm -f .coverage
	$(POETRY_CMD) pytest && (echo "All is well!" > $@)
	@echo "<<< Done."

### - package: packages the project for distribution via PyPI.
package: dist
dist: .build_pytest_report
	@echo ">>> Packaging BAD client..."
	poetry build
	@echo "<<< Done."

### - debug: creates a test installation for debugging purposes.
.PHONY: debug
debug: $(BUILD_SOURCES) $(SRC_DIR) .build_pytest_report
	@echo ">>> Creating installation directory..."
	test -d $(INSTALL_DIR) || mkdir $(INSTALL_DIR)
	@echo ">>> Starting debug session..."
	@cd $(INSTALL_DIR) && poetry shell
	rm -rf $(INSTALL_DIR)
	@echo "<<< Done."

### - push-test: pushes the package to Test PyPI.
push-test: .build_pypi_report
.build_pypi_report: .build_pytest_report dist
	@echo ">>> Pushing to Test PyPI..."
	-rm -f $@
	twine check dist/* && twine upload --repository testpypi dist/* && \
	  (echo "Push test was good!" > $@)
	@echo "<<< Done."

### - push: pushes the package to PyPI.
push: .build_pypi_report
	@echo ">>> Pushing to PyPI..."
	twine check dist/* && twine upload dist/*
	@echo "<<< Done."

### - clean: cleans project directory.
.PHONY: clean
clean:
	@echo ">>> Cleaning project directory..."
	-rm -f ./*~  # Removes Emacs backup files
	-rm -f .coverage
	-rm -f .build_*
	-rm -rf $(INSTALL_DIR)
	-rm -rf docsrc/_build
	-rm -rf dist
	-pyenv uninstall -f $(VENV_NAME)
	@echo "<<< Done."

### - help: displays this message.
.PHONY: help
help:
	@echo "This project's Makefile supports the following targets:"
	@grep '[#]##' Makefile | sed 's/[#]##//g'

# Disable Makefile update via implicit rules
Makefile: ;
