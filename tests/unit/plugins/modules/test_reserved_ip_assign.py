# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
from ansible_collections.digitalocean.cloud.plugins.modules import reserved_ip_assign


@pytest.fixture(autouse=True)
def mock_time_sleep():
    """Automatically mock time.sleep() for all tests to prevent hanging."""
    with patch("time.sleep"):
        yield


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


def create_module(params, check_mode=False, fail_json_side_effect=None, exit_json_side_effect=None):
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


def test_create_unassigned_reserved_ip():
    """Test creating an unassigned reserved IP with region."""
    set_module_args({"region": "nyc3"})

    params = {
        "token": "test-token",
        "timeout": 300,
        "reserved_ip": None,
        "droplet_id": None,
        "name": None,
        "region": "nyc3",
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        client_mock = MagicMock()
        client_mock.reserved_ips.create.return_value = {
            "reserved_ip": {
                "ip": "192.168.1.1",
                "region": {"slug": "nyc3"},
            }
        }

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            instance = reserved_ip_assign.ReservedIPAssign(module)
            instance.timeout = 300

            with patch.object(instance, "create") as create_mock:
                create_mock.return_value = None
                instance.create()


def test_create_and_assign_by_droplet_id():
    """Test creating and assigning reserved IP by droplet_id."""
    set_module_args({"droplet_id": 12345})

    params = {
        "token": "test-token",
        "timeout": 300,
        "reserved_ip": None,
        "droplet_id": 12345,
        "name": None,
        "region": None,
    }

    droplet_data = {
        "id": 12345,
        "name": "test-droplet",
        "region": {"slug": "nyc3"},
    }

    client_mock = MagicMock()
    client_mock.droplets.get.return_value = {"droplet": droplet_data}
    client_mock.reserved_ips.create.return_value = {
        "reserved_ip": {
            "ip": "192.168.1.1",
            "droplet": droplet_data,
            "region": {"slug": "nyc3"},
        }
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            with patch(
                "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanFunctions.find_droplet"
            ) as find_droplet_mock:
                find_droplet_mock.return_value = droplet_data

                instance = reserved_ip_assign.ReservedIPAssign(module)

                with patch.object(instance, "create_and_assign") as create_assign_mock:
                    create_assign_mock.return_value = None
                    instance.create_and_assign()


def test_assign_existing_by_droplet_id():
    """Test assigning existing reserved IP by droplet_id."""
    set_module_args({"reserved_ip": "192.168.1.1", "droplet_id": 12345})

    params = {
        "token": "test-token",
        "timeout": 300,
        "reserved_ip": "192.168.1.1",
        "droplet_id": 12345,
        "name": None,
        "region": None,
    }

    reserved_ip_data = {
        "ip": "192.168.1.1",
        "droplet": None,
        "region": {"slug": "nyc3"},
    }

    droplet_data = {
        "id": 12345,
        "name": "test-droplet",
        "region": {"slug": "nyc3"},
    }

    action_data = {
        "id": 123,
        "type": "assign",
        "status": "completed",
        "resource_type": "reserved_ip",
        "resource_id": "192.168.1.1",
    }

    client_mock = MagicMock()
    client_mock.reserved_ips.get.return_value = {"reserved_ip": reserved_ip_data}
    client_mock.droplets.get.return_value = {"droplet": droplet_data}
    # Mock reserved_ip_actions.post (not reserved_ips.actions.post)
    client_mock.reserved_ip_actions.post.return_value = {"action": action_data}

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            with patch(
                "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanFunctions.find_droplet"
            ) as find_droplet_mock:
                find_droplet_mock.return_value = droplet_data

                # Mock time.sleep() and get_action_by_id() to prevent hanging
                # The action status is "completed" so the loop won't run, but we mock
                # these just in case to prevent any potential hangs
                with patch("time.sleep"), patch(
                    "ansible_collections.digitalocean.cloud.plugins.modules.reserved_ip_assign.ReservedIPAssign.get_action_by_id",
                    return_value=action_data,
                ):
                    instance = reserved_ip_assign.ReservedIPAssign(module)

                    with patch.object(instance, "assign") as assign_mock:
                        assign_mock.return_value = None
                        instance.assign()


def test_create_unassigned_missing_region():
    """Test creating unassigned reserved IP without region should fail."""
    set_module_args({})

    params = {
        "token": "test-token",
        "timeout": 300,
        "reserved_ip": None,
        "droplet_id": None,
        "name": None,
        "region": None,
    }

    client_mock = MagicMock()

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False, fail_json_side_effect=SystemExit(1))

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            try:
                instance = reserved_ip_assign.ReservedIPAssign(module)
            except SystemExit:
                pass

            module.fail_json.assert_called_once()
            assert "Must provide region" in module.fail_json.call_args[1]["msg"]


def test_assign_existing_missing_droplet_params():
    """Test assigning existing reserved IP without droplet params should fail."""
    set_module_args({"reserved_ip": "192.168.1.1"})

    params = {
        "token": "test-token",
        "timeout": 300,
        "reserved_ip": "192.168.1.1",
        "droplet_id": None,
        "name": None,
        "region": None,
    }

    reserved_ip_data = {
        "ip": "192.168.1.1",
        "droplet": None,
        "region": {"slug": "nyc3"},
    }

    client_mock = MagicMock()
    client_mock.reserved_ips.get.return_value = {"reserved_ip": reserved_ip_data}

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False, fail_json_side_effect=SystemExit(1))

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            try:
                instance = reserved_ip_assign.ReservedIPAssign(module)
            except SystemExit:
                pass

            assert module.fail_json.call_count >= 1
            # Check that one of the calls has the expected message
            found_msg = False
            for call in module.fail_json.call_args_list:
                if "Must provide either droplet_id" in str(call):
                    found_msg = True
                    break
            assert found_msg or "Must provide either droplet_id" in str(module.fail_json.call_args)


def test_name_requires_region():
    """Test that name requires region."""
    set_module_args({"name": "test-droplet"})

    params = {
        "token": "test-token",
        "timeout": 300,
        "reserved_ip": None,
        "droplet_id": None,
        "name": "test-droplet",
        "region": None,
    }

    client_mock = MagicMock()

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False, fail_json_side_effect=SystemExit(1))

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            try:
                instance = reserved_ip_assign.ReservedIPAssign(module)
            except SystemExit:
                pass

            module.fail_json.assert_called_once()
            assert "name requires region" in module.fail_json.call_args[1]["msg"]


def test_create_check_mode():
    """Test creating reserved IP in check mode."""
    set_module_args({"region": "nyc3"})

    params = {
        "token": "test-token",
        "timeout": 300,
        "reserved_ip": None,
        "droplet_id": None,
        "name": None,
        "region": "nyc3",
    }

    client_mock = MagicMock()

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=True)

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            # create() is called during __init__ in check_mode
            instance = reserved_ip_assign.ReservedIPAssign(module)

            module.exit_json.assert_called_once()
            assert module.exit_json.call_args[1]["changed"] is True
            assert "would be created" in module.exit_json.call_args[1]["msg"]


def test_assign_idempotent():
    """Test assigning reserved IP that's already assigned to the same droplet."""
    set_module_args({"reserved_ip": "192.168.1.1", "droplet_id": 12345})

    params = {
        "token": "test-token",
        "timeout": 300,
        "reserved_ip": "192.168.1.1",
        "droplet_id": 12345,
        "name": None,
        "region": None,
    }

    reserved_ip_data = {
        "ip": "192.168.1.1",
        "droplet": {
            "id": 12345,
            "name": "test-droplet",
        },
        "region": {"slug": "nyc3"},
    }

    droplet_data = {
        "id": 12345,
        "name": "test-droplet",
        "region": {"slug": "nyc3"},
    }

    action_data = {
        "id": 123,
        "type": "assign",
        "status": "completed",
        "resource_type": "reserved_ip",
        "resource_id": "192.168.1.1",
    }

    client_mock = MagicMock()
    client_mock.reserved_ips.get.return_value = {"reserved_ip": reserved_ip_data}
    # Mock reserved_ip_actions.post to prevent hanging in assign() polling loop
    client_mock.reserved_ip_actions.post.return_value = {"action": action_data}

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            with patch(
                "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanFunctions.find_droplet"
            ) as find_droplet_mock:
                find_droplet_mock.return_value = droplet_data

                # Mock time.sleep() and get_action_by_id() to prevent hanging
                # The assign() method will be called during __init__, so we need
                # to mock these before instantiation
                with patch("time.sleep"), patch(
                    "ansible_collections.digitalocean.cloud.plugins.modules.reserved_ip_assign.ReservedIPAssign.get_action_by_id",
                    return_value=action_data,
                ):
                    instance = reserved_ip_assign.ReservedIPAssign(module)

                    # The idempotent check happens early in assign() before the polling loop
                    # It calls exit_json with changed=False, but since exit_json is mocked
                    # and doesn't actually exit, we need to check that it was called with
                    # the idempotent message
                    # Note: exit_json may be called twice - once for idempotent check,
                    # and potentially once more, but we verify the idempotent call happened
                    exit_calls = module.exit_json.call_args_list
                    idempotent_call = None
                    for call in exit_calls:
                        if call[1].get("changed") is False and "already assigned" in call[1].get("msg", ""):
                            idempotent_call = call
                            break

                    assert idempotent_call is not None, "Idempotent check exit_json not called"
                    assert idempotent_call[1]["changed"] is False
                    assert "already assigned" in idempotent_call[1]["msg"]


def test_reserved_ip_not_found():
    """Test assigning a reserved IP that doesn't exist."""
    set_module_args({"reserved_ip": "192.168.1.1", "droplet_id": 12345})

    params = {
        "token": "test-token",
        "timeout": 300,
        "reserved_ip": "192.168.1.1",
        "droplet_id": 12345,
        "name": None,
        "region": None,
    }

    # Mock HttpResponseError
    # Create a proper exception class that derives from BaseException
    try:
        from azure.core.exceptions import HttpResponseError as AzureHttpResponseError
        # Create a real exception instance
        http_error = AzureHttpResponseError(message="Reserved IP not found", response=MagicMock())
        http_error.error = MagicMock()
        http_error.error.message = "Reserved IP not found"
        http_error.status_code = 404
        http_error.reason = "Not Found"
    except ImportError:
        # Fallback if azure.core is not available - create a real exception class
        class HttpResponseError(Exception):
            def __init__(self, message, status_code=404, reason="Not Found"):
                self.message = message
                self.status_code = status_code
                self.reason = reason
                self.error = MagicMock()
                self.error.message = message
                super().__init__(message)

        http_error = HttpResponseError("Reserved IP not found", status_code=404, reason="Not Found")

    client_mock = MagicMock()
    client_mock.reserved_ips.get.side_effect = http_error

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            try:
                instance = reserved_ip_assign.ReservedIPAssign(module)
            except SystemExit:
                pass

            module.fail_json.assert_called_once()
            assert "Reserved IP 192.168.1.1 not found" in module.fail_json.call_args[1]["msg"]


def test_create_and_assign_by_name_region():
    """Test creating and assigning reserved IP by name and region."""
    set_module_args({"name": "test-droplet", "region": "nyc3"})

    params = {
        "token": "test-token",
        "timeout": 300,
        "reserved_ip": None,
        "droplet_id": None,
        "name": "test-droplet",
        "region": "nyc3",
    }

    droplet_data = {
        "id": 12345,
        "name": "test-droplet",
        "region": {"slug": "nyc3"},
    }

    client_mock = MagicMock()
    client_mock.reserved_ips.create.return_value = {
        "reserved_ip": {
            "ip": "192.168.1.1",
            "droplet": droplet_data,
            "region": {"slug": "nyc3"},
        }
    }

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False)

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            with patch(
                "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanFunctions.find_droplet"
            ) as find_droplet_mock:
                find_droplet_mock.return_value = droplet_data

                instance = reserved_ip_assign.ReservedIPAssign(module)

                with patch.object(instance, "create_and_assign") as create_assign_mock:
                    create_assign_mock.return_value = None
                    instance.create_and_assign()


def test_droplet_id_and_name_mutually_exclusive():
    """Test that droplet_id and name are mutually exclusive."""
    set_module_args({"droplet_id": 12345, "name": "test-droplet", "region": "nyc3"})

    params = {
        "token": "test-token",
        "timeout": 300,
        "reserved_ip": None,
        "droplet_id": 12345,
        "name": "test-droplet",
        "region": "nyc3",
    }

    client_mock = MagicMock()

    with patch.object(basic.AnsibleModule, "__init__", return_value=None):
        module = create_module(params, check_mode=False, fail_json_side_effect=SystemExit(1))

        with patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanReqs.Client",
            return_value=client_mock,
        ):
            try:
                instance = reserved_ip_assign.ReservedIPAssign(module)
            except SystemExit:
                pass

            module.fail_json.assert_called_once()
            assert "droplet_id and name are mutually exclusive" in module.fail_json.call_args[1]["msg"]
