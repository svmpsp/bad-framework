#!/usr/bin/env make

PYTHON_VERSION ?= 3.6.9
VENV_DIR ?= venv-bad-framework
INSTALL_DIR ?= test_install
PACKAGE_NAME ?= bad_framework

# If --python is not specified virtualenv uses the /usr/bin/python interpreter
PYTHON ?= $(shell which python3)
BUILD_PYTHON ?= $(VENV_DIR)/bin/python3

.PHONY: clean docs package push push-test test

all: package

.python-version:
	@echo ">>> Setting project Python version..."
	pyenv local $(PYTHON_VERSION)
	@echo ">>> Done."

$(VENV_DIR)/bin/activate: requirements.txt .python-version
	@echo ">>> Creating virtual environment..."
	virtualenv --python=$(PYTHON) $(VENV_DIR)
	source $(VENV_DIR)/bin/activate && \
		$(BUILD_PYTHON) -m pip install --upgrade pip && \
		$(BUILD_PYTHON) -m pip install -r requirements.txt
	@echo ">>> Done."

docs: $(VENV_DIR)/bin/activate
	@echo ">>> Creating project documentation..."
	source $(VENV_DIR)/bin/activate && $(MAKE) -C docs html
	@echo "<<< Done"

test: setup.py $(VENV_DIR)/bin/activate
	@echo ">>> Running tests..."
	source $(VENV_DIR)/bin/activate && $(BUILD_PYTHON) -m unittest -v --catch --failfast --locals
	@echo ">>> Done."

package: test $(VENV_DIR)/bin/activate
	@echo ">>> Packaging BAD client..."
	source $(VENV_DIR)/bin/activate && $(BUILD_PYTHON) setup.py sdist bdist_wheel
	@echo ">>> Done."

install-test: $(VENV_DIR)/bin/activate
	@echo ">>> Creating test installation..."
	source $(VENV_DIR)/bin/activate && pip install --no-cache-dir -e ../bad-client && test -d $(INSTALL_DIR) || mkdir $(INSTALL_DIR) && cd $(INSTALL_DIR) \
        && bad init && bash
	@echo ">>> Done."

push-test: dist package $(VENV_DIR)/bin/activate
	@echo ">>> Pushing to Test PyPI..."
	source $(VENV_DIR)/bin/activate && twine check dist/* && twine upload --repository testpypi dist/*
	@echo ">>> Done."

push: dist package $(VENV_DIR)/bin/activate
	@echo ">>> Pushing to PyPI..."
	source $(VENV_DIR)/bin/activate && twine check dist/* && twine upload dist/*
	@echo ">>> Done."

clean:
	@echo ">>> Cleaning project directory..."
	rm -rf ./*~
	rm -rf .python-version
	rm -rf $(VENV_DIR)
	rm -rf $(INSTALL_DIR)
	rm -rf build
	rm -rf $(PACKAGE_NAME).egg-info
	rm -rf dist
	@echo ">>> Done."

# Disable Makefile update via implicit rules
Makefile: ;
