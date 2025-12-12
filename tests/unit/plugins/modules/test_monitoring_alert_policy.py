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

from ansible_collections.digitalocean.cloud.plugins.modules import (
    monitoring_alert_policy,
)


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


def get_default_params():
    """Return default parameters for monitoring alert policy."""
    return {
        "token": "test-token",
        "state": "present",
        "alerts": {
            "email": ["test@example.com"],
            "slack": [],
        },
        "compare": "GreaterThan",
        "description": "CPU Alert",
        "enabled": True,
        "entities": ["12345"],
        "tags": ["production"],
        "type": "v1/insights/droplet/cpu",
        "value": 80.0,
        "window": "5m",
    }


def get_sample_policy():
    """Return sample policy response from API."""
    return {
        "uuid": "test-uuid-12345",
        "alerts": {
            "email": ["test@example.com"],
            "slack": [],
        },
        "compare": "GreaterThan",
        "description": "CPU Alert",
        "enabled": True,
        "entities": ["12345"],
        "tags": ["production"],
        "type": "v1/insights/droplet/cpu",
        "value": 80.0,
        "window": "5m",
    }


def test_create_monitoring_alert_policy_success():
    """Test successful monitoring alert policy creation with correct description field."""
    params = get_default_params()
    set_module_args(params)

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # No existing policies
        client_mock.monitoring.list_alert_policy.return_value = {"policies": []}
        # Create returns the new policy
        client_mock.monitoring.create_alert_policy.return_value = {
            "policy": get_sample_policy()
        }

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            monitoring_alert_policy.MonitoringAlertPolicy(module)

            # Verify create_alert_policy was called with correct body
            client_mock.monitoring.create_alert_policy.assert_called_once()
            call_kwargs = client_mock.monitoring.create_alert_policy.call_args[1]
            body = call_kwargs["body"]

            # Key assertion: verify "description" key (not "desciption" typo)
            assert "description" in body
            assert body["description"] == "CPU Alert"

            # Verify exit_json was called with changed=True
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is True
            assert "Created monitoring alert policy" in call_args["msg"]
            assert call_args["policy"]["uuid"] == "test-uuid-12345"


def test_monitoring_alert_policy_exists_idempotent():
    """Test monitoring alert policy already exists - idempotent behavior with description match."""
    params = get_default_params()
    set_module_args(params)

    existing_policy = get_sample_policy()

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # Policy already exists with matching description
        client_mock.monitoring.list_alert_policy.return_value = {
            "policies": [existing_policy]
        }

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            monitoring_alert_policy.MonitoringAlertPolicy(module)

            # Verify exit_json was called with changed=False
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is False
            assert "exists" in call_args["msg"]
            assert call_args["policy"]["uuid"] == "test-uuid-12345"

            # Verify create was NOT called (idempotent)
            assert not client_mock.monitoring.create_alert_policy.called


def test_monitoring_alert_policy_different_description_creates_new():
    """Test that different description creates new policy (not idempotent)."""
    params = get_default_params()
    set_module_args(params)

    # Existing policy has different description
    existing_policy = get_sample_policy()
    existing_policy["description"] = "Different Description"

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # Policy exists but with different description
        client_mock.monitoring.list_alert_policy.return_value = {
            "policies": [existing_policy]
        }
        # Create returns new policy
        client_mock.monitoring.create_alert_policy.return_value = {
            "policy": get_sample_policy()
        }

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            monitoring_alert_policy.MonitoringAlertPolicy(module)

            # Should create new policy since description doesn't match
            assert client_mock.monitoring.create_alert_policy.called
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is True


def test_monitoring_alert_policy_multiple_exists():
    """Test multiple matching policies exist - graceful handling."""
    params = get_default_params()
    set_module_args(params)

    policy1 = get_sample_policy()
    policy1["uuid"] = "uuid-1"
    policy2 = get_sample_policy()
    policy2["uuid"] = "uuid-2"

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # Multiple matching policies exist
        client_mock.monitoring.list_alert_policy.return_value = {
            "policies": [policy1, policy2]
        }

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            monitoring_alert_policy.MonitoringAlertPolicy(module)

            # Verify exit_json was called with changed=False
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is False
            assert "2" in call_args["msg"]  # Message mentions count


def test_delete_monitoring_alert_policy_success():
    """Test successful monitoring alert policy deletion."""
    params = get_default_params()
    params["state"] = "absent"
    set_module_args(params)

    existing_policy = get_sample_policy()

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # Policy exists
        client_mock.monitoring.list_alert_policy.return_value = {
            "policies": [existing_policy]
        }
        # Delete succeeds
        client_mock.monitoring.delete_alert_policy.return_value = None

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            monitoring_alert_policy.MonitoringAlertPolicy(module)

            # Verify delete was called
            client_mock.monitoring.delete_alert_policy.assert_called_once_with(
                alert_uuid="test-uuid-12345"
            )

            # Verify exit_json was called with changed=True
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is True
            assert "Deleted" in call_args["msg"]


def test_delete_monitoring_alert_policy_not_found():
    """Test deletion when policy doesn't exist - idempotent behavior."""
    params = get_default_params()
    params["state"] = "absent"
    set_module_args(params)

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        # No policies
        client_mock.monitoring.list_alert_policy.return_value = {"policies": []}

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            monitoring_alert_policy.MonitoringAlertPolicy(module)

            # Verify exit_json was called with changed=False
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is False
            assert "does not exist" in call_args["msg"]


def test_create_monitoring_alert_policy_check_mode():
    """Test policy creation in check mode."""
    params = get_default_params()
    set_module_args(params)

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=True)

        client_mock = MagicMock()
        # No existing policies
        client_mock.monitoring.list_alert_policy.return_value = {"policies": []}

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            monitoring_alert_policy.MonitoringAlertPolicy(module)

            # Verify exit_json was called with changed=True
            assert module.exit_json.called
            call_args = module.exit_json.call_args[1]
            assert call_args["changed"] is True
            assert "would be created" in call_args["msg"]

            # Verify create was NOT called in check mode
            assert not client_mock.monitoring.create_alert_policy.called


def test_create_monitoring_alert_policy_http_error():
    """Test policy creation when API raises HttpResponseError."""
    params = get_default_params()
    set_module_args(params)

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        # Create HttpResponseError
        http_error = HttpResponseError()
        http_error.status_code = 422
        http_error.reason = "Unprocessable Entity"
        http_error.error = MagicMock()
        http_error.error.message = "Invalid alert policy"

        client_mock = MagicMock()
        # No existing policies
        client_mock.monitoring.list_alert_policy.return_value = {"policies": []}
        # Create raises HttpResponseError
        client_mock.monitoring.create_alert_policy.side_effect = http_error

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ), patch.object(
            monitoring_alert_policy.DigitalOceanCommonModule,
            "HttpResponseError",
            HttpResponseError,
        ):
            monitoring_alert_policy.MonitoringAlertPolicy(module)

            # Verify fail_json was called
            assert module.fail_json.called
            call_args = module.fail_json.call_args[1]
            assert call_args["changed"] is False
            assert "Invalid alert policy" in call_args["msg"]
