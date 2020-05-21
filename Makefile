#!/usr/bin/env make

PYTHON_VERSION ?= 3.7.5
PACKAGE_NAME ?= bad_framework
VENV_NAME := $(PACKAGE_NAME)-$(PYTHON_VERSION)
INSTALL_DIR ?= install

.PHONY: clean package push-test push test venv

all: package

.python-version:
	@echo ">>> Setting project Python version..."
	pyenv virtualenv $(PYTHON_VERSION) $(VENV_NAME)
	pyenv local $(VENV_NAME)
	@echo "<<< Done."

venv: .python-version requirements.txt
	@echo ">>> Updating venv dependencies..."
	pip install -U pip
	pip install -r requirements.txt
	pip install -e .
	@echo "<<< Done."

docs: .python-version venv
	@echo ">>> Creating project documentation..."
	$(MAKE) -C docsrc html
	cp -a ./docsrc/_build/html/. ./docs
	@echo "<<< Done"

test: setup.py venv
	@echo ">>> Running tests..."
	python3 -m unittest -v --catch --failfast --locals
	@echo "<<< Done."

package: docs venv test
	@echo ">>> Packaging BAD client..."
	python3 setup.py sdist bdist_wheel
	@echo "<<< Done."

install: package
	@echo ">>> Creating installation directory..."
	pip install -e .
	[[ -d $(INSTALL_DIR) ]] || mkdir $(INSTALL_DIR)
	@echo ">>> Starting debug session..."
	@cd $(INSTALL_DIR) && bash
	rm -rf $(INSTALL_DIR)
	@echo "<<< Done."

push-test: dist package
	@echo ">>> Pushing to Test PyPI..."
	twine check dist/* && twine upload --repository testpypi dist/*
	@echo "<<< Done."

push: dist package
	@echo ">>> Pushing to PyPI..."
	twine check dist/* && twine upload dist/*
	@echo "<<< Done."

clean:
	@echo ">>> Cleaning project directory..."
	rm -rf ./*~
	rm -rf .python-version
	pyenv uninstall -f $(VENV_NAME)
	rm -rf $(INSTALL_DIR)
	rm -rf build
	rm -rf docsrc/_build
	rm -rf $(PACKAGE_NAME).egg-info
	rm -rf dist
	@echo "<<< Done."

# Disable Makefile update via implicit rules
Makefile: ;
