VENV = .venv
PYTHON_CMD ?= python3.11
PROJECT_NAME ?= baking-test
QUAY_ORG ?= $(USER)

venv_check:
ifndef VIRTUAL_ENV
	$(error Not in a virtual environment)
endif

venv_create:
ifndef VIRTUAL_ENV
	$(PYTHON_CMD) -m venv $(VENV)
	@echo "Virtual environment $(VENV) created, activate running: source $(VENV)/bin/activate"
else
	$(warning VIRTUAL_ENV variable present, already within a virtual environment?)
endif

setup: venv_check
	python -m pip install cookiecutter
	rm -rf $(PROJECT_NAME)
	cookiecutter . project_name=$(PROJECT_NAME) quay_org=$(QUAY_ORG) --no-input

test: venv_check setup
	cd $(PROJECT_NAME) && make -f Makefile test

run: venv_check setup
	cd $(PROJECT_NAME) && make -f Makefile run

coverage: venv_check setup
	cd $(PROJECT_NAME) && make -f Makefile coverage
