#!/usr/bin/env make

PYTHON_VERSION ?= 3.7.5
PACKAGE_NAME ?= bad_framework
VENV_NAME := $(PACKAGE_NAME)-$(PYTHON_VERSION)

SRC_DIR ?= bad_framework
TEST_DIR ?= tests
INSTALL_DIR ?= install

SOURCES ?= $(shell find $(PACKAGE_NAME))
TEST_SOURCES ?= pytest.ini $(shell find tests)
DOC_SOURCES ?= $(shell find docsrc | grep -v `_`)

.PHONY: clean help

all: package

### - venv: creates the virtualenvironment for the project.
venv: .python-version
.python-version: requirements.txt setup.py
	@echo ">>> Creating project development venv..."
	-pyenv uninstall -f $(VENV_NAME)
	pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME)
	pyenv local $(VENV_NAME)
	pip install -U pip wheel setuptools
	pip install -r requirements.txt
	pip install -e .
	@echo "<<< Done."

### - docs: builds the documentation.
docs: $(DOC_SOURCES) .python-version
	@echo ">>> Creating project documentation..."
	$(MAKE) -C docsrc html
	cp -a ./docsrc/_build/html/. ./docs
	@echo "<<< Done"

### - test: runs unit and integration tests.
test: .pytest_report
.pytest_report: $(TEST_SOURCES) $(SOURCES) .python-version
	@echo ">>> Running tests..."
	-rm -f .pytest_report
	-rm -f .coverage
	pytest && (echo "All is well!" > .pytest_report)
	@echo "<<< Done."

### - package: packages the project for distribution via PyPI.
package: dist
dist: .python-version .pytest_report docs
	@echo ">>> Packaging BAD client..."
	python3 setup.py sdist bdist_wheel
	@echo "<<< Done."

### - debug: creates a test installation for debugging purposes.
debug: $(SRC_DIR) .pytest_report
	@echo ">>> Creating installation directory..."
	[[ -d $(INSTALL_DIR) ]] || mkdir $(INSTALL_DIR)
	@echo ">>> Starting debug session..."
	pip install -e .
	@cd $(INSTALL_DIR) && bash
	rm -rf $(INSTALL_DIR)
	@echo "<<< Done."

### - push-test: pushes the package to Test PyPI.
push-test: .pypi_report
.pypi_report: .python-version .pytest_report dist
	@echo ">>> Pushing to Test PyPI..."
	-rm -f .pipy_report
	twine check dist/* && twine upload --repository testpypi dist/* && (echo "Push test was good!" > .pypi_report)
	@echo "<<< Done."

### - push: pushes the package to PyPI.
push: .pypi_report
	@echo ">>> Pushing to PyPI..."
	twine check dist/* && twine upload dist/*
	@echo "<<< Done."

### - clean: cleans project directory.
clean:
	@echo ">>> Cleaning project directory..."
	-rm -f ./*~  # Removes Emacs backup files
	-rm -f .coverage
	-rm -f .pytest_report
	-rm -f .pypi_report
	-rm -f .python-version
	-rm -rf $(INSTALL_DIR)
	-rm -rf build
	-rm -rf docsrc/_build
	-rm -rf $(PACKAGE_NAME).egg-info
	-rm -rf dist
	-pyenv uninstall -f $(VENV_NAME)
	@echo "<<< Done."

### - help: displays this message.
help:
	@echo "This project's Makefile supports the following targets:"
	@grep '[#]##' Makefile | sed 's/[#]##//g'

# Disable Makefile update via implicit rules
Makefile: ;
