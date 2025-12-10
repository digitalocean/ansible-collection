# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import sys
from unittest.mock import MagicMock, patch
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes


# Create a custom Exception class for HttpResponseError
class HttpResponseError(Exception):
    """Mock HttpResponseError exception"""

    pass


# Mock the required imports before importing the module
sys.modules["pydo"] = MagicMock()
azure_mock = MagicMock()
azure_core_mock = MagicMock()
azure_exceptions_mock = MagicMock()
# Set HttpResponseError as a real Exception class, not a MagicMock
azure_exceptions_mock.HttpResponseError = HttpResponseError
azure_core_mock.exceptions = azure_exceptions_mock
azure_mock.core = azure_core_mock
sys.modules["azure"] = azure_mock
sys.modules["azure.core"] = azure_core_mock
sys.modules["azure.core.exceptions"] = azure_exceptions_mock

from ansible_collections.digitalocean.cloud.plugins.modules import ssh_key


def set_module_args(args):
    """Helper function to set module arguments."""
    args = args or {}
    args["_ansible_remote_tmp"] = "/tmp"
    args["_ansible_keep_remote_files"] = False

    default_args = {
        "token": "test-token",
    }
    default_args.update(args)

    basic._ANSIBLE_ARGS = to_bytes(
        basic.json.dumps({"ANSIBLE_MODULE_ARGS": default_args})
    )


def create_module(
    params, check_mode=False, fail_json_side_effect=None, exit_json_side_effect=None
):
    """Helper function to create a properly mocked AnsibleModule.

    Note: This must be called within a 'with patch.object(basic.AnsibleModule, "__init__", return_value=None):' context.
    """
    module = basic.AnsibleModule(argument_spec={})
    module.params = params
    module.check_mode = check_mode
    module._debug = False
    module._verbosity = 0
    if fail_json_side_effect is not None:
        module.fail_json = MagicMock(side_effect=fail_json_side_effect)
    else:
        module.fail_json = MagicMock()
    if exit_json_side_effect is not None:
        module.exit_json = MagicMock(side_effect=exit_json_side_effect)
    else:
        module.exit_json = MagicMock()
    return module


def create_mock_error(status_code, message):
    """Helper function to create a mock HttpResponseError."""
    error = MagicMock()
    error.status_code = status_code
    error.reason = "Test Reason"
    error.error = MagicMock()
    error.error.message = message
    return error


def test_create_ssh_key_success():
    """Test successful SSH key creation."""
    set_module_args(
        {
            "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
            "name": "Test SSH Key",
        }
    )

    params = {
        "token": "test-token",
        "state": "present",
        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
        "name": "Test SSH Key",
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # No existing SSH keys with the same name
        client_mock.ssh_keys.list.return_value = {"ssh_keys": []}
        # Create returns the new SSH key
        client_mock.ssh_keys.create.return_value = {
            "ssh_key": {
                "id": 12345,
                "name": "Test SSH Key",
                "fingerprint": "3b:16:bf:e4:8b:00:8b:b8:59:8c:a9:d3:f0:19:45:fa",
                "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
            }
        }

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            ssh_key.SSHKey(module)

            # Verify exit_json was called with changed=True
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is True
            assert "Created SSH key" in call_args["msg"]
            assert (
                call_args["ssh_key"]["fingerprint"]
                == "3b:16:bf:e4:8b:00:8b:b8:59:8c:a9:d3:f0:19:45:fa"
            )


def test_create_ssh_key_already_exists_by_public_key_in_create():
    """Test SSH key creation when public key already exists (422 error during create)."""
    set_module_args(
        {
            "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
            "name": "New Name",
        }
    )

    params = {
        "token": "test-token",
        "state": "present",
        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
        "name": "New Name",
    }

    existing_ssh_key = {
        "id": 12345,
        "name": "Existing SSH Key",
        "fingerprint": "3b:16:bf:e4:8b:00:8b:b8:59:8c:a9:d3:f0:19:45:fa",
        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        # Create a proper HttpResponseError mock
        http_error = HttpResponseError()
        http_error.status_code = 422
        http_error.reason = "Unprocessable Entity"
        http_error.error = MagicMock()
        http_error.error.message = "SSH Key is already in use on your account"

        client_mock = MagicMock()
        # First call to list() in get_ssh_keys() returns no keys with matching name
        # Second call to list() in present() fails to find the key (edge case)
        # Third call to list() in create_ssh_key() exception handler finds the key
        call_count = [0]

        def list_side_effect():
            call_count[0] += 1
            if call_count[0] <= 2:
                # First two calls: return empty list (simulating the key not being found initially)
                return {"ssh_keys": []}
            else:
                # Third call in the exception handler: return the existing key
                return {"ssh_keys": [existing_ssh_key]}

        client_mock.ssh_keys.list.side_effect = list_side_effect
        # Create fails with 422 error
        client_mock.ssh_keys.create.side_effect = http_error

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ), patch.object(
            ssh_key.DigitalOceanCommonModule, "HttpResponseError", HttpResponseError
        ):
            ssh_key.SSHKey(module)

            # Verify exit_json was called with changed=False
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is False
            assert "already exists" in call_args["msg"]
            assert call_args["ssh_key"]["id"] == 12345


def test_ssh_key_exists_by_name():
    """Test SSH key already exists by name - idempotent behavior."""
    set_module_args(
        {
            "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
            "name": "Test SSH Key",
        }
    )

    params = {
        "token": "test-token",
        "state": "present",
        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
        "name": "Test SSH Key",
    }

    existing_ssh_key = {
        "id": 12345,
        "name": "Test SSH Key",
        "fingerprint": "3b:16:bf:e4:8b:00:8b:b8:59:8c:a9:d3:f0:19:45:fa",
        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # SSH key with the same name exists
        client_mock.ssh_keys.list.return_value = {"ssh_keys": [existing_ssh_key]}

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            ssh_key.SSHKey(module)

            # Verify exit_json was called with changed=False
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is False
            assert "exists" in call_args["msg"]
            assert call_args["ssh_key"]["id"] == 12345


def test_delete_ssh_key_success():
    """Test successful SSH key deletion."""
    set_module_args(
        {
            "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
            "name": "Test SSH Key",
            "state": "absent",
        }
    )

    params = {
        "token": "test-token",
        "state": "absent",
        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
        "name": "Test SSH Key",
    }

    existing_ssh_key = {
        "id": 12345,
        "name": "Test SSH Key",
        "fingerprint": "3b:16:bf:e4:8b:00:8b:b8:59:8c:a9:d3:f0:19:45:fa",
        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # SSH key exists
        client_mock.ssh_keys.list.return_value = {"ssh_keys": [existing_ssh_key]}
        # Delete succeeds
        client_mock.ssh_keys.delete.return_value = None

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            ssh_key.SSHKey(module)

            # Verify exit_json was called with changed=True
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is True
            assert "Deleted SSH key" in call_args["msg"]


def test_delete_ssh_key_not_found():
    """Test SSH key deletion when key doesn't exist - idempotent behavior."""
    set_module_args(
        {
            "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
            "name": "Test SSH Key",
            "state": "absent",
        }
    )

    params = {
        "token": "test-token",
        "state": "absent",
        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
        "name": "Test SSH Key",
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # No SSH keys with the name
        client_mock.ssh_keys.list.return_value = {"ssh_keys": []}

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            ssh_key.SSHKey(module)

            # Verify exit_json was called with changed=False
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is False
            assert "does not exist" in call_args["msg"]


def test_create_ssh_key_check_mode():
    """Test SSH key creation in check mode."""
    set_module_args(
        {
            "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
            "name": "Test SSH Key",
        }
    )

    params = {
        "token": "test-token",
        "state": "present",
        "public_key": "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC...",
        "name": "Test SSH Key",
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=True)

        client_mock = MagicMock()
        # No existing SSH keys with the same name or public key
        client_mock.ssh_keys.list.return_value = {"ssh_keys": []}

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            ssh_key.SSHKey(module)

            # Verify exit_json was called with changed=True
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is True
            assert "would be created" in call_args["msg"]
            # Verify create was NOT called in check mode
            assert not client_mock.ssh_keys.create.called
