#######################################
#                                     #
#   Static Routes Operator Makefile   #
#                                     #
#######################################

KUBECTL_CMD         ?= kubectl
MKDIR_CMD           ?= mkdir
PYTHON3_CMD         ?= python3
PIP3_CMD            ?= pip3
VIRTUALENV_CMD      ?= virtualenv
PYTEST_CMD          ?= pytest
KOPF_CMD            ?= kopf

VENV_FOLDER               ?= .venv
CONTROLLER_PATH           ?= controller
CONTROLLER_NAME           ?= static-route-operator
API_CRD_PATH              ?= $(CONTROLLER_PATH)/config
API_GENERATOR_SCRIPT      ?= $(CONTROLLER_PATH)/generate_api.py
PROJ_REQUIREMENTS_FILE    ?= requirements.txt
DEV_REQUIREMENTS_FILE     ?= requirements-dev.txt

VERSION_MANIFEST    ?= VERSION
PROJECT_VERSION     ?= $(shell cat $(VERSION_MANIFEST))
ORGANIZATION        ?= digitalocean
IMAGE_NAME          ?= $(CONTROLLER_NAME)
IMAGE_TAG           ?= $(ORGANIZATION)/$(IMAGE_NAME):v$(PROJECT_VERSION)

PROJECT_MAJOR_VERSION  ?= $(shell echo $(PROJECT_VERSION) | cut -f1 -d.)
RELEASES_FOLDER        ?= releases


.ONESHELL:
ENV_PREFIX=$(shell python3 -c "if __import__('pathlib').Path('$(VENV_FOLDER)/bin/$(PIP3_CMD)').exists(): print('$(VENV_FOLDER)/bin/')")

.PHONY: install-venv-package
install-venv-package:
	@echo "Installing virtualenv Python package ..."
	@$(PIP3_CMD) install virtualenv

.PHONY: create-venv
create-venv: install-venv-package
	@echo "Creating $(VENV_FOLDER) virtual environment ..."
	@$(VIRTUALENV_CMD) $(VENV_FOLDER)

.PHONY: install
install: create-venv
	@echo "Installing project dependencies into $(VENV_FOLDER) virtual environment ..."
	@$(ENV_PREFIX)$(PIP3_CMD) install -r $(PROJ_REQUIREMENTS_FILE)

.PHONY: manifests
manifests: install
	@echo "Generating CRD manifests into $(API_CRD_PATH) for project version $(PROJECT_VERSION) ..."
	@$(ENV_PREFIX)$(PYTHON3_CMD) $(API_GENERATOR_SCRIPT) \
		--output-path $(API_CRD_PATH)

.PHONY: release
release: manifests
	@echo "Generating new release manifests for project version $(PROJECT_VERSION) ..."
	@$(MKDIR_CMD) -p $(RELEASES_FOLDER)/v$(PROJECT_MAJOR_VERSION)
	@$(KUBECTL_CMD) kustomize $(CONTROLLER_PATH) > \
		$(RELEASES_FOLDER)/v$(PROJECT_MAJOR_VERSION)/$(CONTROLLER_NAME)-v$(PROJECT_VERSION).yaml

.PHONY: docker_image
docker_image:
	@echo "Building static routes operator Docker image with version $(PROJECT_VERSION) ..."
	@docker build -t $(IMAGE_TAG) .

.PHONY: dev-install
dev-install: create-venv
	@echo "Installing project dependencies into $(VENV_FOLDER) virtual environment ..."
	@$(ENV_PREFIX)$(PIP3_CMD) install -r $(DEV_REQUIREMENTS_FILE)

.PHONY: test
test: dev-install
	@echo "Starting Pytests for the static routes operator ..."
	@$(ENV_PREFIX)/$(PYTEST_CMD)

.PHONY: clean
clean:
	@echo "Cleaning up python $(VENV_FOLDER) virtual environment ..."
	@rm -rf $(VENV_FOLDER)
