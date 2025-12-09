# -*- coding: utf-8 -*-
# Copyright: (c) 2025, DigitalOcean LLC <ansible-noreply@digitalocean.com>
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

    def __init__(self, message="", status_code=None, reason=""):
        super().__init__(message)
        self.error = MagicMock()
        self.error.message = message
        self.status_code = status_code
        self.reason = reason


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

from ansible_collections.digitalocean.cloud.plugins.module_utils.droplet_resize import (
    DropletResize,
)
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
)


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


class TestDropletResize:
    """Test cases for DropletResize class"""

    def test_resize_droplet_success(
        self, mock_module, mock_client, sample_droplet, sample_action
    ):
        """Test successful droplet resize with action polling"""
        # Setup: mock the API responses
        mock_client.droplet_actions.post.return_value = {"action": sample_action}
        mock_client.actions.get.return_value = {"action": sample_action}
        mock_client.droplets.get.return_value = {
            "droplet": {**sample_droplet, "size": {"slug": "s-2vcpu-2gb"}}
        }

        # Create DropletResize instance
        with patch.object(DigitalOceanCommonModule, "__init__", return_value=None):
            dr = DropletResize.__new__(DropletResize)
            dr.module = mock_module
            dr.client = mock_client
            dr.droplet_id = 123456
            dr.current_size = "s-1vcpu-1gb"
            dr.new_size = "s-2vcpu-2gb"
            dr.resize_disk = True
            dr.region = "nyc3"
            dr.timeout = 300

            # Execute resize
            with pytest.raises(AnsibleExitJson) as exc:
                dr.resize_droplet()

            # Verify results
            result = exc.value.args[0]
            assert result["changed"] is True
            assert "Resized Droplet test-droplet" in result["msg"]
            assert result["action"]["status"] == "completed"
            assert result["droplet"]["size"]["slug"] == "s-2vcpu-2gb"

            # Verify API calls
            mock_client.droplet_actions.post.assert_called_once_with(
                droplet_id=123456,
                body={"type": "resize", "size": "s-2vcpu-2gb", "disk": True},
            )
            mock_client.droplets.get.assert_called_once_with(123456)

    def test_resize_droplet_action_polling(
        self, mock_module, mock_client, sample_droplet, sample_action
    ):
        """Test that action status is polled until completion"""
        # Setup: action starts in-progress, then completes
        in_progress_action = {**sample_action, "status": "in-progress"}
        completed_action = {**sample_action, "status": "completed"}

        mock_client.droplet_actions.post.return_value = {"action": in_progress_action}
        # First call returns in-progress, second call returns completed
        mock_client.actions.get.side_effect = [
            {"action": in_progress_action},
            {"action": completed_action},
        ]
        mock_client.droplets.get.return_value = {
            "droplet": {**sample_droplet, "size": {"slug": "s-2vcpu-2gb"}}
        }

        with patch.object(
            DigitalOceanCommonModule, "__init__", return_value=None
        ), patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.droplet_resize.time"
        ) as mock_time_module:
            # Mock time functions
            # First call: calculate end_time
            # Second call: enter while loop (in-progress)
            # Third call: check again after getting completed action
            mock_time_module.monotonic.side_effect = [0, 0, 0, 0]
            mock_time_module.sleep.return_value = None

            dr = DropletResize.__new__(DropletResize)
            dr.module = mock_module
            dr.client = mock_client
            dr.droplet_id = 123456
            dr.current_size = "s-1vcpu-1gb"
            dr.new_size = "s-2vcpu-2gb"
            dr.resize_disk = False
            dr.region = "nyc3"
            dr.timeout = 300

            with pytest.raises(AnsibleExitJson) as exc:
                dr.resize_droplet()

            result = exc.value.args[0]
            assert result["changed"] is True
            assert result["action"]["status"] == "completed"

            # Verify action was polled multiple times
            assert mock_client.actions.get.call_count == 2
            mock_client.actions.get.assert_any_call(action_id=987654)

    def test_resize_droplet_timeout(
        self, mock_module, mock_client, sample_droplet, sample_action
    ):
        """Test resize timeout when action doesn't complete"""
        # Setup: action remains in-progress
        in_progress_action = {**sample_action, "status": "in-progress"}

        mock_client.droplet_actions.post.return_value = {"action": in_progress_action}
        mock_client.actions.get.return_value = {"action": in_progress_action}

        with patch.object(
            DigitalOceanCommonModule, "__init__", return_value=None
        ), patch(
            "ansible_collections.digitalocean.cloud.plugins.module_utils.droplet_resize.time"
        ) as mock_time_module:
            # Mock both monotonic and sleep
            mock_time_module.monotonic.side_effect = [
                0,
                0,
                301,
            ]  # Start, loop check, then timeout
            mock_time_module.sleep.return_value = None

            dr = DropletResize.__new__(DropletResize)
            dr.module = mock_module
            dr.client = mock_client
            dr.droplet_id = 123456
            dr.current_size = "s-1vcpu-1gb"
            dr.new_size = "s-2vcpu-2gb"
            dr.resize_disk = True
            dr.region = "nyc3"
            dr.timeout = 300

            with pytest.raises(AnsibleFailJson) as exc:
                dr.resize_droplet()

            result = exc.value.args[0]
            assert result["failed"] is True
            assert result["changed"] is True
            assert "has not completed" in result["msg"]
            assert result["action"]["status"] == "in-progress"

    def test_resize_droplet_api_error(self, mock_module, mock_client):
        """Test resize handles API errors properly"""
        # Setup: API returns error
        mock_client.droplet_actions.post.side_effect = HttpResponseError(
            message="Invalid size", status_code=422, reason="Unprocessable Entity"
        )

        with patch.object(
            DigitalOceanCommonModule, "__init__", return_value=None
        ), patch.object(
            DigitalOceanCommonModule, "HttpResponseError", HttpResponseError
        ):
            dr = DropletResize.__new__(DropletResize)
            dr.module = mock_module
            dr.client = mock_client
            dr.droplet_id = 123456
            dr.current_size = "s-1vcpu-1gb"
            dr.new_size = "invalid-size"
            dr.resize_disk = True
            dr.region = "nyc3"
            dr.timeout = 300

            with pytest.raises(AnsibleFailJson) as exc:
                dr.resize_droplet()

            result = exc.value.args[0]
            assert result["failed"] is True
            assert result["changed"] is False
            assert result["msg"] == "Invalid size"
            assert result["error"]["Status Code"] == 422
