# Contributing

Refer to the [Contributing guidelines](https://github.com/ansible/community-docs/blob/main/contributing.rst).

## Local development environment

At a high level, developing on Ansible collections requires a specific directory
structure, setting environment variables accordingly, and having Python and the
various collection dependencies available and configured. Generally, Ansible
collection testing includes: `sanity`, `unit`, and `integration`. Warning, the
latter, `integration`, will turn up real resources in the DigitalOcean cloud,
and will cost real money.

> There is also a [devcontainer](./.devcontainer/devcontainer.json) configuration.

```shell
# Create a directory structure for the checkout, ansible-test looks for
# collections with grandparent named ansible_collections
mkdir -p "${HOME}/src/ansible_collections/digitalocean"

# Clone this repository
git clone git@github.com:digitalocean/ansible-collection.git \
  "${HOME}/src/ansible_collections/digitalocean/cloud"

# Change directory to the checkout
cd "${HOME}/src/ansible_collections/digitalocean/cloud"

# Optional: install Poetry https://python-poetry.org and set up this repository
# and its requirements (having a consistent and dedicated Python environment
# is generally quite helpful)
poetry shell
poetry install

# Configure Ansible for Poetry's python and set Ansible's collection search path
export ANSIBLE_PYTHON_INTERPRETER="$(which python3)"

# Place this checkout first so that the checkout modules are accessible first
# The last two directories in this example are fairly standard, but, your
# default COLLECTIONS_PATHS may be different, consult: ansible-config dump
export ANSIBLE_COLLECTIONS_PATHS="../..:${HOME}/.ansible/collections:/usr/share/ansible/collections"

# Optional: Set YAML output (requires the community.general collection)
export ANSIBLE_STDOUT_CALLBACK="community.general.yaml"

# Optional: For VS Code setting "python.envFile": "${workspaceFolder}/.env"
if ! test -f .env; then
  echo 'PYTHONPATH="../../.."' | tee .env
fi

# Run the sanity and units tests for this collection
ansible-test sanity --python 3.9 --verbose
ansible-test units --python 3.9 --verbose

# Set up the configuration file for integration tests
cp tests/integration/integration_config.yml.template \
  tests/integration/integration_config.yml

# Update tests/integration/integration_config.yml and update accordingly
# You can set pr_number to any number (pr_number: 0 should work just fine)
# The purpose of this variable is for the integration tests which run in
# GitHub. It is possible that there are multiple open pull requests in this
# repository at the same time, and as such, using the pull request number
# is a simple way to give the Cloud resources unique names. In this example
# we are setting things up for local development, and as such, the number 0
# works just fine. Do not commit tests/integration/integration_config.yml
#
# Example:
# ---
# digitalocean_token: <Your DigitalOcean API token>
# aws_access_key_id: <Your Spaces Key ID>
# aws_secret_access_key: <Your Spaces Secret Key>
# pr_number: 0
#
# Running the integration tests will create real resources and cost real money
ansible-test integration --python 3.9 --verbose # To test all modules
ansible-test integration --python 3.9 account_info --verbose # Test a single module
```
