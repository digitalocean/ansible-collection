# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
import sys
from unittest.mock import MagicMock, patch
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
import json


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

from ansible_collections.digitalocean.cloud.plugins.modules import droplet_action_resize


def set_module_args(args):
    """Prepare arguments so that they will be picked up during module creation"""
    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


class AnsibleExitJson(Exception):
    """Exception class to be raised by module.exit_json and caught by the test case"""

    pass


class AnsibleFailJson(Exception):
    """Exception class to be raised by module.fail_json and caught by the test case"""

    pass


def exit_json(*args, **kwargs):
    """Function to patch over exit_json; package return data into an exception"""
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    """Function to patch over fail_json; package return data into an exception"""
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


@pytest.fixture
def mock_module():
    """Fixture to create a mock AnsibleModule"""
    mock = MagicMock()
    mock.check_mode = False
    mock.exit_json = exit_json
    mock.fail_json = fail_json
    mock.params = {
        "timeout": 300,
        "token": "fake-token",
        "name": "test-droplet",
        "region": "nyc3",
        "droplet_id": None,
        "size": "s-2vcpu-2gb",
        "resize_disk": False,
    }
    return mock


@pytest.fixture
def mock_client():
    """Fixture to create a mock DigitalOcean client"""
    mock = MagicMock()
    return mock


@pytest.fixture
def sample_droplet():
    """Fixture to create a sample droplet"""
    return {
        "id": 123456,
        "name": "test-droplet",
        "region": {"slug": "nyc3", "name": "New York 3"},
        "status": "active",
        "size": {"slug": "s-1vcpu-1gb"},
    }


@pytest.fixture
def sample_action():
    """Fixture to create a sample action"""
    return {
        "id": 987654,
        "type": "resize",
        "status": "completed",
        "started_at": "2023-01-01T00:00:00Z",
        "completed_at": "2023-01-01T00:01:00Z",
    }


class TestDropletActionResizeFindDroplet:
    """Test cases for finding droplets with multiple matches"""

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanFunctions.get_droplet_by_name_in_region"
    )
    def test_multiple_droplets_error_message(
        self, mock_get_droplets, mock_module, mock_client, sample_droplet
    ):
        """Test that multiple droplets returns error with droplet IDs"""
        droplet_1 = sample_droplet.copy()
        droplet_1["id"] = 123456
        droplet_2 = sample_droplet.copy()
        droplet_2["id"] = 789012
        mock_get_droplets.return_value = [droplet_1, droplet_2]

        with patch.object(
            droplet_action_resize.DigitalOceanCommonModule,
            "__init__",
            return_value=None,
        ):
            resize_obj = droplet_action_resize.DropletActionResize.__new__(
                droplet_action_resize.DropletActionResize
            )
            resize_obj.module = mock_module
            resize_obj.client = mock_client
            resize_obj.name = "test-droplet"
            resize_obj.region = "nyc3"
            resize_obj.droplet_id = None
            resize_obj.size = "s-2vcpu-2gb"
            resize_obj.resize_disk = False

            with pytest.raises(AnsibleFailJson) as exc:
                resize_obj.find_droplet()

            result = exc.value.args[0]
            assert result["failed"] is True
            assert "currently 2 Droplets" in result["msg"]
            assert "123456" in result["msg"]
            assert "789012" in result["msg"]

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanFunctions.get_droplet_by_name_in_region"
    )
    def test_single_droplet_found(
        self, mock_get_droplets, mock_module, mock_client, sample_droplet
    ):
        """Test that single droplet is returned correctly"""
        mock_get_droplets.return_value = [sample_droplet]

        with patch.object(
            droplet_action_resize.DigitalOceanCommonModule,
            "__init__",
            return_value=None,
        ):
            resize_obj = droplet_action_resize.DropletActionResize.__new__(
                droplet_action_resize.DropletActionResize
            )
            resize_obj.module = mock_module
            resize_obj.client = mock_client
            resize_obj.name = "test-droplet"
            resize_obj.region = "nyc3"
            resize_obj.droplet_id = None
            resize_obj.size = "s-2vcpu-2gb"
            resize_obj.resize_disk = False

            result = resize_obj.find_droplet()

            assert result == sample_droplet
            assert result["id"] == 123456

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanFunctions.get_droplet_by_name_in_region"
    )
    def test_no_droplet_found(self, mock_get_droplets, mock_module, mock_client):
        """Test that no droplet returns error"""
        mock_get_droplets.return_value = []

        with patch.object(
            droplet_action_resize.DigitalOceanCommonModule,
            "__init__",
            return_value=None,
        ):
            resize_obj = droplet_action_resize.DropletActionResize.__new__(
                droplet_action_resize.DropletActionResize
            )
            resize_obj.module = mock_module
            resize_obj.client = mock_client
            resize_obj.name = "test-droplet"
            resize_obj.region = "nyc3"
            resize_obj.droplet_id = None
            resize_obj.size = "s-2vcpu-2gb"
            resize_obj.resize_disk = False

            with pytest.raises(AnsibleFailJson) as exc:
                resize_obj.find_droplet()

            result = exc.value.args[0]
            assert result["failed"] is True
            assert "No Droplet named" in result["msg"]
