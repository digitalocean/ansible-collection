#!/usr/bin/make -f

.PHONY: install
install:
	poetry install --with=dev
	poetry run pre-commit install --install-hooks

.PHONY: update
clean:
	poetry update
	poetry run pre-commit autoupdate

.PHONY: lint
lint: collection-cleanup collection-prep
	poetry run ansible-lint

# Assumes ansible-test is available in the global scope, such as within the devcontainer environment
.PHONY: sanity
sanity: collection-cleanup collection-prep
	poetry run tests/run-sanity.sh

.PHONY: integration
integration: collection-cleanup collection-prep
	poetry run tests/run-integration.sh

# Make a copy of the collection available in an expected Ansible path
# For running tooling in Codespaces or other environments
# If you get ansible-lint errors about unresolved modules in this collection,
# run this command then re-run ansible-lint.
.PHONY: collection-prep
collection-prep:
	mkdir -p ~/.ansible/collections/ansible_collections/digitalocean/cloud
	cp -r ./ ~/.ansible/collections/ansible_collections/digitalocean/cloud

.PHONY: collection-cleanup
collection-cleanup:
	rm -rf ~/.ansible/collections/ansible_collections/digitalocean/cloud
