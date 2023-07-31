#!/usr/bin/env make

.PHONY: install
install:
	poetry install --with=dev
	poetry run pre-commit install --install-hooks

.PHONY: update
clean:
	poetry update
	poetry run pre-commit autoupdate

.PHONY: lint
lint: collection-prep
	poetry run ansible-lint --profile=production

# Make a copy of the collection available in an expected Ansible path
# For running tooling in Codespaces or other environments
.PHONY: collection-prep
collection-prep:
	mkdir -p ~/.ansible/collections/ansible_collections/digitalocean/cloud
	cp -r ./ ~/.ansible/collections/ansible_collections/digitalocean/cloud
