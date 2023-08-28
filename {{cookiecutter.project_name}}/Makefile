TEMPDIR_INFOSECTOOLS = /tmp/infosec-dev-tools
VENV=.venv
COVERAGE_REPORT_FORMAT = 'html'
DOCKERFILE ?= Dockerfile
CONTAINER_WEBPORT ?= 8000
HOST_WEBPORT=$(CONTAINER_WEBPORT)
CONTEXT=.
CONTAINER_ENGINE=podman
BONFIRE_CONFIG=".bonfirecfg.yaml"
CLOWDAPP_TEMPLATE ?= clowdapp.yaml
APP_NAME ?= {{cookiecutter.project_name | replace("_", "-")}}
PYTHON_CMD=python3.11
QUAY_ORG ?= $(USER)
QUAY_REPOSITORY ?= $(APP_NAME)
IMAGE=quay.io/$(QUAY_ORG)/$(QUAY_REPOSITORY)

# Determine the container engine
ifneq ($(shell command -v "podman"),)
    CONTAINER_ENGINE = podman
else ifneq ($(shell command -v "docker"),)
    CONTAINER_ENGINE = docker
else
    $(error "No container engine found. Install either podman or docker.")
endif

# Determine IMAGE_TAG and LABEL
BASE_IMAGE_TAG=$(shell git rev-parse --short=7 HEAD)
ifdef ghprbPullId
    IMAGE_TAG=pr-$(ghprbPullId)-$(BASE_IMAGE_TAG)
    LABEL=$(shell echo "--label quay.expires-after=1h")
else ifdef gitlabMergeRequestId
    IMAGE_TAG=mr-$(gitlabMergeRequestId)-$(BASE_IMAGE_TAG)
    LABEL=$(shell echo "--label quay.expires-after=1h")
else
    IMAGE_TAG=$(BASE_IMAGE_TAG)
endif

run: venv_check
	python manage.py runserver

install_pre_commit: venv_check
	# Remove any outdated tools
	rm -rf $(TEMPDIR_INFOSECTOOLS)
	# Clone up-to-date tools
	git clone https://gitlab.corp.redhat.com/infosec-public/developer-workbench/tools.git /tmp/infosec-dev-tools

	# Cleanup installed old tools
	$(TEMPDIR_INFOSECTOOLS)/scripts/uninstall-legacy-tools

	# install pre-commit and configure it on our repo
	make -C $(TEMPDIR_INFOSECTOOLS)/rh-pre-commit install
	python -m rh_pre_commit.multi configure --configure-git-template --force
	python -m rh_pre_commit.multi install --force --path ./

	rm -rf $(TEMPDIR_INFOSECTOOLS)

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

quay_login:
	echo -n "$(QUAY_TOKEN)" | $(CONTAINER_ENGINE) login quay.io --username $(QUAY_USER) --password-stdin

lint: install_dev
	pre-commit run --all

install: venv_check
	python -m pip install -e .

install_dev: venv_check
	python -m pip install -e .[dev]

clean:
	rm -rf __pycache__
	find . -name "*.pyc" -exec rm -f {} \;

test: venv_check install_dev
	python manage.py test

smoke-test: venv_check install_dev
	@echo "Running smoke tests"

coverage: venv_check install_dev
	coverage run --source="." manage.py test
	coverage $(COVERAGE_REPORT_FORMAT)

coverage-ci: COVERAGE_REPORT_FORMAT=xml
coverage-ci: coverage

build-image:
	$(CONTAINER_ENGINE) build -t $(IMAGE):$(IMAGE_TAG) -f $(DOCKERFILE) $(LABEL) $(CONTEXT)

run-container:
	$(CONTAINER_ENGINE) run -it --rm -p $(HOST_WEBPORT):$(CONTAINER_WEBPORT) $(IMAGE):$(IMAGE_TAG) runserver 0.0.0.0:8000

push-image:
	$(CONTAINER_ENGINE) push $(IMAGE):$(IMAGE_TAG)

namespace_check:
ifndef NAMESPACE
	$(error NAMESPACE not defined, please specify a NAMESPACE environment varible)
endif

bonfire_process:
	bonfire process -c $(BONFIRE_CONFIG) $(APP_NAME) -s local \
		-p service/IMAGE=$(IMAGE) -p service/IMAGE_TAG=$(IMAGE_TAG) -n default

bonfire_reserve_namespace:
	@bonfire namespace reserve

bonfire_release_namespace: namespace_check
	bonfire namespace release $(NAMESPACE) -f

bonfire_user_namespaces:
	bonfire namespace list --mine

bonfire_deploy: namespace_check
	bonfire deploy -c $(BONFIRE_CONFIG) $(APP_NAME) -s local \
		-p service/IMAGE=$(IMAGE) -p service/IMAGE_TAG=$(IMAGE_TAG) -n $(NAMESPACE)
