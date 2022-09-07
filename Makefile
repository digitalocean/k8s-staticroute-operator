################################################
#                                              #
#  Kubernetes Static Routes Operator Makefile  #
#                                              #
################################################


# Project related stuff
PROJECT_NAME               ?= k8s-staticroute-operator
ORGANIZATION               ?= digitalocean
VERSION_MANIFEST           ?= VERSION
PROJECT_VERSION            ?= $(shell cat $(VERSION_MANIFEST))
PROJECT_MAJOR_VERSION      ?= $(shell echo $(PROJECT_VERSION) | cut -f1 -d.)
RELEASES_FOLDER            ?= releases
CONTROLLER_PATH            ?= controller
CONTROLLER_CFG_PATH        ?= $(CONTROLLER_PATH)/config
API_GENERATOR_SCRIPT       ?= $(CONTROLLER_PATH)/generate_api.py
OPERATOR_RELEASE_MANIFEST  ?= $(RELEASES_FOLDER)/v$(PROJECT_MAJOR_VERSION)/$(PROJECT_NAME)-v$(PROJECT_VERSION).yaml

# Commands related stuff
KUBECTL_CMD     ?= kubectl
MKDIR_CMD       ?= mkdir
RM_CMD          ?= rm
AWK_CMD         ?= awk
PYTHON3_CMD     ?= python3
PIP3_CMD        ?= pip3
VIRTUALENV_CMD  ?= virtualenv
PYTEST_CMD      ?= pytest
KOPF_CMD        ?= kopf

# Python related stuff
VENV_FOLDER             ?= .venv
PROJ_REQUIREMENTS_FILE  ?= requirements.txt
DEV_REQUIREMENTS_FILE   ?= requirements-dev.txt

# Docker related stuff
CONTROLLER_IMAGE_TAG  ?= $(ORGANIZATION)/$(PROJECT_NAME):v$(PROJECT_VERSION)

# Kubernetes related stuff
CURRENT_K8S_CLUSTER        ?= $(shell $(KUBECTL_CMD) config current-context)


.DEFAULT_GOAL := help

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

.PHONY: dev-install
dev-install: create-venv ## Install dev dependencies using pip.
	@echo "Installing project dependencies into $(VENV_FOLDER) virtual environment ..."
	@$(ENV_PREFIX)$(PIP3_CMD) install -r $(DEV_REQUIREMENTS_FILE)

.PHONY: install
install: create-venv ## Install project dependencies (release).
	@echo "Installing project dependencies into $(VENV_FOLDER) virtual environment ..."
	@$(ENV_PREFIX)$(PIP3_CMD) install -r $(PROJ_REQUIREMENTS_FILE)

.PHONY: docker_image
docker-image: ## Build controller Docker image for the project.
	@echo "Building operator Docker image with version $(PROJECT_VERSION) ..."
	@docker build -t $(CONTROLLER_IMAGE_TAG) .

.PHONY: docker_push
docker-push: docker-image ## Push controller Docker image to Docker Hub.
	@echo "Pushing operator Docker image $(CONTROLLER_IMAGE_TAG) to Docker Hub ..."
	@docker push $(CONTROLLER_IMAGE_TAG)

.PHONY: manifests
manifests: install ## Generate CRD manifests.
	@echo "Generating CRD manifests into $(CONTROLLER_CFG_PATH) for project version $(PROJECT_VERSION) ..."
	@$(ENV_PREFIX)$(PYTHON3_CMD) $(API_GENERATOR_SCRIPT) --output-path $(CONTROLLER_CFG_PATH)

.PHONY: release
release: manifests ## Create release artifacts for the project.
	@echo "Generating new release manifests for project version $(PROJECT_VERSION) ..."
	@$(MKDIR_CMD) -p $(RELEASES_FOLDER)/v$(PROJECT_MAJOR_VERSION)
	@$(KUBECTL_CMD) kustomize $(CONTROLLER_PATH) > $(OPERATOR_RELEASE_MANIFEST)

.PHONY: deploy
deploy: release ## Deploy operator to current Kubernetes cluster (uses kubectl current context).
	@echo "Deploying $(OPERATOR_RELEASE_MANIFEST) to $(CURRENT_K8S_CLUSTER) ..."
	@$(KUBECTL_CMD) apply -f $(OPERATOR_RELEASE_MANIFEST)

.PHONY: uninstall
uninstall: ## Uninstall operator from current Kubernetes cluster (uses kubectl current context).
	@echo "Uninstalling operator from $(CURRENT_K8S_CLUSTER) ..."
	@$(KUBECTL_CMD) delete -f $(OPERATOR_RELEASE_MANIFEST)

.PHONY: test
test: dev-install ## Test the project using PyTest.
	@echo "Starting Pytests for the static routes operator ..."
	@$(ENV_PREFIX)/$(PYTEST_CMD)

.PHONY: clean
clean: ## Clean project generated files.
	@echo "Cleaning up python $(VENV_FOLDER) virtual environment ..."
	@$(RM_CMD) -rf $(VENV_FOLDER)

.PHONY: help
help: ## Display this help
	@$(AWK_CMD) 'BEGIN { \
		FS = ":.*##"; \
		printf "\nUsage:\n  make \033[36m<target>\033[0m\n\nTargets:\n" \
	} /^[a-zA-Z_-]+:.*?##/ \
	{ printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 }' \
	$(MAKEFILE_LIST)
