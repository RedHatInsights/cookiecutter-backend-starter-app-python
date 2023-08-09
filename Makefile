VENV=.venv

venv_check:
ifndef VIRTUAL_ENV
	$(error Not in a virtual environment)
endif

install: venv_check
	python -m pip install cookiecutter
	-rm -rf baking-test
	cookiecutter . --no-input

venv_create:
ifndef VIRTUAL_ENV
	python -m venv $(VENV)
	@echo "Virtual environment $(VENV) created, activate running: source $(VENV)/bin/activate"
else
	$(warning VIRTUAL_ENV variable present, already within a virtual environment?)
endif

test: venv_check
	make install
	cd baking-test && make -f Makefile test

run: venv_check
	make install
	cd baking-test && make -f Makefile run

coverage: venv_check
	make install
	cd baking-test && make -f Makefile coverage
