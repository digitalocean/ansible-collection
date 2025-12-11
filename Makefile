#!/usr/bin/make -f

.PHONY: install
install:
	uv sync --all-groups
	uv run pre-commit install --install-hooks

.PHONY: update
update:
	uv lock --upgrade
	uv run pre-commit autoupdate

.PHONY: format
format:
	uv run ruff format .

.PHONY: check
check:
	uv run ruff check --fix .

.PHONY: lint
lint: collection-cleanup collection-prep
	uv run antsibull-changelog lint
	uv run ansible-lint --fix

# Assumes ansible-test is available in the global scope, such as within the devcontainer environment
.PHONY: sanity
sanity: collection-cleanup collection-prep
	uv run tests/run-sanity.sh $(filter-out $@,$(MAKECMDGOALS))

.PHONY: integration
integration: collection-cleanup collection-prep
	uv run tests/run-integration.sh $(filter-out $@,$(MAKECMDGOALS))

.PHONY: units
units: collection-cleanup collection-prep
	uv run tests/run-units.sh $(filter-out $@,$(MAKECMDGOALS))

# Run unit tests with coverage collection
.PHONY: units-coverage
units-coverage: collection-cleanup collection-prep
	uv run tests/run-units.sh --coverage

# Generate coverage reports after running units-coverage
.PHONY: coverage-report
coverage-report:
	uv run ansible-test coverage combine
	uv run ansible-test coverage report

# Generate HTML coverage report (open tests/output/reports/coverage/index.html)
.PHONY: coverage-html
coverage-html:
	uv run ansible-test coverage combine
	uv run ansible-test coverage html
	@echo "HTML report: tests/output/reports/coverage/index.html"

# Generate XML coverage report for CI/CD (codecov, etc.)
.PHONY: coverage-xml
coverage-xml:
	uv run ansible-test coverage combine
	uv run ansible-test coverage xml
	@echo "XML report: tests/output/reports/coverage.xml"

# Clean coverage data
.PHONY: coverage-clean
coverage-clean:
	uv run ansible-test coverage erase
	rm -rf tests/output/coverage tests/output/reports/coverage*

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

# Prevent Make from treating integration test targets as make targets
# This allows commands like: make integration reserved_ip_assign
%:
	@:
