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

from ansible_collections.digitalocean.cloud.plugins.modules import tag


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
    """Helper function to create a properly mocked AnsibleModule."""
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


def test_create_tag_success():
    """Test successful tag creation."""
    set_module_args(
        {
            "name": "production",
        }
    )

    params = {
        "token": "test-token",
        "state": "present",
        "name": "production",
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # No existing tags
        client_mock.tags.list.return_value = {"tags": []}
        # Create returns the new tag
        client_mock.tags.create.return_value = {
            "tag": {
                "name": "production",
                "resources": {
                    "count": 0,
                    "droplets": {"count": 0},
                    "images": {"count": 0},
                    "volumes": {"count": 0},
                    "volume_snapshots": {"count": 0},
                    "databases": {"count": 0},
                },
            }
        }

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            tag.Tag(module)

            # Verify exit_json was called with changed=True
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is True
            assert "Created tag" in call_args["msg"]
            assert call_args["tag"]["name"] == "production"


def test_create_tag_invalid_name_error_response():
    """Test tag creation with invalid name - validation function rejects it."""
    import pytest

    # Test the validation function directly
    with pytest.raises(ValueError) as exc_info:
        tag.Tag._validate_tag_name("infra.domain.tld")

    # Verify the error message contains the expected text
    assert "dots are not allowed" in str(exc_info.value)

    # Test various invalid tag names
    with pytest.raises(ValueError, match="must be a non-empty string"):
        tag.Tag._validate_tag_name("")

    with pytest.raises(ValueError, match="255 characters or fewer"):
        tag.Tag._validate_tag_name("a" * 256)

    with pytest.raises(ValueError, match="invalid characters"):
        tag.Tag._validate_tag_name("tag with spaces")

    with pytest.raises(ValueError, match="invalid characters"):
        tag.Tag._validate_tag_name("tag@special")


def test_create_tag_http_error():
    """Test tag creation when API raises HttpResponseError."""
    set_module_args(
        {
            "name": "test-tag",
        }
    )

    params = {
        "token": "test-token",
        "state": "present",
        "name": "test-tag",
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        # Create HttpResponseError
        http_error = HttpResponseError()
        http_error.status_code = 422
        http_error.reason = "Unprocessable Entity"
        http_error.error = MagicMock()
        http_error.error.message = "Invalid tag name"

        client_mock = MagicMock()
        # No existing tags
        client_mock.tags.list.return_value = {"tags": []}
        # Create raises HttpResponseError
        client_mock.tags.create.side_effect = http_error

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ), patch.object(
            tag.DigitalOceanCommonModule, "HttpResponseError", HttpResponseError
        ):
            tag.Tag(module)

            # Verify fail_json was called
            assert module.fail_json.called
            call_args = module.fail_json.call_args[1]
            assert call_args["changed"] is False
            assert "Invalid tag name" in call_args["msg"]


def test_tag_exists_idempotent():
    """Test tag already exists - idempotent behavior."""
    set_module_args(
        {
            "name": "production",
        }
    )

    params = {
        "token": "test-token",
        "state": "present",
        "name": "production",
    }

    existing_tag = {
        "name": "production",
        "resources": {
            "count": 5,
            "droplets": {"count": 5},
            "images": {"count": 0},
            "volumes": {"count": 0},
            "volume_snapshots": {"count": 0},
            "databases": {"count": 0},
        },
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # Tag already exists
        client_mock.tags.list.return_value = {"tags": [existing_tag]}

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            tag.Tag(module)

            # Verify exit_json was called with changed=False
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is False
            assert "exists" in call_args["msg"]
            assert call_args["tag"]["name"] == "production"


def test_delete_tag_success():
    """Test successful tag deletion."""
    set_module_args(
        {
            "name": "production",
            "state": "absent",
        }
    )

    params = {
        "token": "test-token",
        "state": "absent",
        "name": "production",
    }

    existing_tag = {
        "name": "production",
        "resources": {"count": 0},
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # Tag exists
        client_mock.tags.list.return_value = {"tags": [existing_tag]}
        # Delete succeeds
        client_mock.tags.delete.return_value = None

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            tag.Tag(module)

            # Verify exit_json was called with changed=True
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is True
            assert "Deleted tag" in call_args["msg"]


def test_delete_tag_not_found():
    """Test tag deletion when tag doesn't exist - idempotent behavior."""
    set_module_args(
        {
            "name": "production",
            "state": "absent",
        }
    )

    params = {
        "token": "test-token",
        "state": "absent",
        "name": "production",
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # No tags
        client_mock.tags.list.return_value = {"tags": []}

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            tag.Tag(module)

            # Verify exit_json was called with changed=False
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is False
            assert "does not exist" in call_args["msg"]


def test_create_tag_check_mode():
    """Test tag creation in check mode."""
    set_module_args(
        {
            "name": "production",
        }
    )

    params = {
        "token": "test-token",
        "state": "present",
        "name": "production",
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=True)

        client_mock = MagicMock()
        # No existing tags
        client_mock.tags.list.return_value = {"tags": []}

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            tag.Tag(module)

            # Verify exit_json was called with changed=True
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is True
            assert "would be created" in call_args["msg"]
            # Verify create was NOT called in check mode
            assert not client_mock.tags.create.called
