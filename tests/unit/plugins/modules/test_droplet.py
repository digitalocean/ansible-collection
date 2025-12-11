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

from ansible_collections.digitalocean.cloud.plugins.modules import droplet


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
        "state": "present",
        "timeout": 300,
        "token": "fake-token",
        "name": "test-droplet",
        "region": "nyc3",
        "size": "s-1vcpu-1gb",
        "image": "ubuntu-20-04-x64",
        "ssh_keys": [],
        "backups": False,
        "ipv6": False,
        "monitoring": False,
        "resize": False,
        "resize_disk": False,
        "tags": [],
        "user_data": None,
        "volumes": [],
        "vpc_uuid": None,
        "with_droplet_agent": False,
        "unique_name": False,
        "client_override_options": None,
        "module_override_options": None,
        "droplet_id": None,
    }
    return mock


@pytest.fixture
def mock_client():
    """Fixture to create a mock DigitalOcean client"""
    client = MagicMock()
    return client


@pytest.fixture
def sample_droplet():
    """Fixture providing a sample droplet response"""
    return {
        "id": 123456,
        "name": "test-droplet",
        "status": "active",
        "region": {"slug": "nyc3", "name": "New York 3"},
        "size": {"slug": "s-1vcpu-1gb"},
        "image": {"slug": "ubuntu-20-04-x64"},
    }


class TestDropletGetMethods:
    """Test class for get methods in Droplet module"""

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.DigitalOceanFunctions.get_paginated"
    )
    def test_get_droplets_by_name_and_region_empty(
        self, mock_get_paginated, mock_module, mock_client
    ):
        """Test get_droplets_by_name_and_region returns empty list when no droplets exist"""
        mock_module.params["unique_name"] = True
        mock_get_paginated.return_value = []

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"

            result = droplet_obj.get_droplets_by_name_and_region()

            assert result == []
            # Verify that params is empty dict (the fix for issue #250)
            mock_get_paginated.assert_called_once()
            call_args = mock_get_paginated.call_args
            assert call_args[1]["params"] == dict()

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.DigitalOceanFunctions.get_paginated"
    )
    def test_get_droplets_by_name_and_region_single_match(
        self, mock_get_paginated, mock_module, mock_client, sample_droplet
    ):
        """Test get_droplets_by_name_and_region returns single matching droplet"""
        mock_module.params["unique_name"] = True
        mock_get_paginated.return_value = [sample_droplet]

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"

            result = droplet_obj.get_droplets_by_name_and_region()

            assert len(result) == 1
            assert result[0]["id"] == 123456

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.DigitalOceanFunctions.get_paginated"
    )
    def test_get_droplets_by_name_and_region_filters_by_region(
        self, mock_get_paginated, mock_module, mock_client, sample_droplet
    ):
        """Test get_droplets_by_name_and_region filters out droplets in different regions"""
        droplet_nyc = sample_droplet.copy()
        droplet_sfo = sample_droplet.copy()
        droplet_sfo["region"] = {"slug": "sfo2", "name": "San Francisco 2"}

        mock_get_paginated.return_value = [droplet_nyc, droplet_sfo]

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"

            result = droplet_obj.get_droplets_by_name_and_region()

            assert len(result) == 1
            assert result[0]["region"]["slug"] == "nyc3"

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.DigitalOceanFunctions.get_paginated"
    )
    def test_get_droplets_by_name_and_region_filters_by_name(
        self, mock_get_paginated, mock_module, mock_client, sample_droplet
    ):
        """Test get_droplets_by_name_and_region filters out droplets with different names"""
        droplet_test = sample_droplet.copy()
        droplet_other = sample_droplet.copy()
        droplet_other["name"] = "other-droplet"

        mock_get_paginated.return_value = [droplet_test, droplet_other]

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"

            result = droplet_obj.get_droplets_by_name_and_region()

            assert len(result) == 1
            assert result[0]["name"] == "test-droplet"

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.DigitalOceanFunctions.get_paginated"
    )
    def test_get_droplets_by_name_and_region_multiple_matches(
        self, mock_get_paginated, mock_module, mock_client, sample_droplet
    ):
        """Test get_droplets_by_name_and_region returns multiple droplets with same name and region"""
        droplet_1 = sample_droplet.copy()
        droplet_2 = sample_droplet.copy()
        droplet_2["id"] = 789012

        mock_get_paginated.return_value = [droplet_1, droplet_2]

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"

            result = droplet_obj.get_droplets_by_name_and_region()

            assert len(result) == 2

    def test_get_droplet_by_id_success(self, mock_module, mock_client, sample_droplet):
        """Test get_droplet_by_id returns droplet when it exists"""
        mock_client.droplets.get.return_value = {"droplet": sample_droplet}

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client

            result = droplet_obj.get_droplet_by_id(123456)

            assert result["id"] == 123456
            mock_client.droplets.get.assert_called_once_with(droplet_id=123456)

    def test_get_droplet_by_id_not_found(self, mock_module, mock_client):
        """Test get_droplet_by_id returns None when droplet doesn't exist"""
        mock_client.droplets.get.return_value = {"droplet": None}

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client

            result = droplet_obj.get_droplet_by_id(999999)

            assert result is None


class TestDropletPresent:
    """Test class for present state in Droplet module"""

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.create_droplet"
    )
    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.get_droplets_by_name_and_region"
    )
    def test_present_unique_name_creates_when_none_exist(
        self, mock_get_droplets, mock_create, mock_module, mock_client
    ):
        """Test present with unique_name creates droplet when none exist"""
        mock_module.params["unique_name"] = True
        mock_module.check_mode = False
        mock_get_droplets.return_value = []

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.state = "present"
            droplet_obj.unique_name = True
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"

            try:
                droplet_obj.present()
            except AnsibleExitJson:
                pass

            mock_get_droplets.assert_called_once()
            assert mock_create.called

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.get_droplets_by_name_and_region"
    )
    def test_present_unique_name_exists_no_changes(
        self, mock_get_droplets, mock_module, mock_client, sample_droplet
    ):
        """Test present with unique_name returns existing droplet without changes"""
        mock_module.params["unique_name"] = True
        mock_get_droplets.return_value = [sample_droplet]

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.state = "present"
            droplet_obj.unique_name = True
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"
            droplet_obj.resize = False

            with pytest.raises(AnsibleExitJson) as exc:
                droplet_obj.present()

            result = exc.value.args[0]
            assert result["changed"] is False
            assert "exists" in result["msg"]

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.get_droplets_by_name_and_region"
    )
    def test_present_unique_name_multiple_droplets_fails(
        self, mock_get_droplets, mock_module, mock_client, sample_droplet
    ):
        """Test present with unique_name fails when multiple droplets exist"""
        mock_module.params["unique_name"] = True
        droplet_1 = sample_droplet.copy()
        droplet_2 = sample_droplet.copy()
        droplet_2["id"] = 789012
        mock_get_droplets.return_value = [droplet_1, droplet_2]

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.state = "present"
            droplet_obj.unique_name = True
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"

            with pytest.raises(AnsibleFailJson) as exc:
                droplet_obj.present()

            result = exc.value.args[0]
            assert result["failed"] is True
            assert "currently 2 Droplets" in result["msg"]

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.create_droplet"
    )
    def test_present_check_mode(self, mock_create, mock_module, mock_client):
        """Test present in check mode doesn't create droplet"""
        mock_module.check_mode = True
        mock_module.params["unique_name"] = False

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.state = "present"
            droplet_obj.unique_name = False
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"

            with pytest.raises(AnsibleExitJson) as exc:
                droplet_obj.present()

            result = exc.value.args[0]
            assert result["changed"] is True
            assert "would be created" in result["msg"]
            mock_create.assert_not_called()


class TestDropletAbsent:
    """Test class for absent state in Droplet module"""

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.delete_droplet"
    )
    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.get_droplets_by_name_and_region"
    )
    def test_absent_unique_name_deletes_existing(
        self, mock_get_droplets, mock_delete, mock_module, mock_client, sample_droplet
    ):
        """Test absent with unique_name deletes existing droplet"""
        mock_module.params["unique_name"] = True
        mock_module.check_mode = False
        mock_get_droplets.return_value = [sample_droplet]
        # Make delete_droplet raise AnsibleExitJson to simulate normal behavior
        mock_delete.side_effect = AnsibleExitJson({"changed": True, "msg": "Deleted"})

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.state = "absent"
            droplet_obj.unique_name = True
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"
            droplet_obj.droplet_id = None

            try:
                droplet_obj.absent()
            except AnsibleExitJson:
                pass

            mock_get_droplets.assert_called_once()
            mock_delete.assert_called_once_with(sample_droplet)

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.get_droplets_by_name_and_region"
    )
    def test_absent_unique_name_not_found(
        self, mock_get_droplets, mock_module, mock_client
    ):
        """Test absent with unique_name returns ok when droplet doesn't exist"""
        mock_module.params["unique_name"] = True
        mock_get_droplets.return_value = []

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.state = "absent"
            droplet_obj.unique_name = True
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"

            with pytest.raises(AnsibleExitJson) as exc:
                droplet_obj.absent()

            result = exc.value.args[0]
            assert result["changed"] is False
            assert "not found" in result["msg"]

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.get_droplets_by_name_and_region"
    )
    def test_absent_unique_name_multiple_droplets_fails(
        self, mock_get_droplets, mock_module, mock_client, sample_droplet
    ):
        """Test absent with unique_name fails when multiple droplets exist"""
        mock_module.params["unique_name"] = True
        droplet_1 = sample_droplet.copy()
        droplet_2 = sample_droplet.copy()
        droplet_2["id"] = 789012
        mock_get_droplets.return_value = [droplet_1, droplet_2]

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.state = "absent"
            droplet_obj.unique_name = True
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"

            with pytest.raises(AnsibleFailJson) as exc:
                droplet_obj.absent()

            result = exc.value.args[0]
            assert result["failed"] is True
            assert "currently 2 Droplets" in result["msg"]

    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.delete_droplet"
    )
    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.get_droplet_by_id"
    )
    def test_absent_by_id(
        self, mock_get_by_id, mock_delete, mock_module, mock_client, sample_droplet
    ):
        """Test absent with droplet_id deletes by ID"""
        mock_module.params["unique_name"] = False
        mock_module.params["droplet_id"] = 123456
        mock_get_by_id.return_value = sample_droplet

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.state = "absent"
            droplet_obj.unique_name = False
            droplet_obj.droplet_id = 123456

            try:
                droplet_obj.absent()
            except AnsibleExitJson:
                pass

            mock_get_by_id.assert_called_once_with(123456)
            mock_delete.assert_called_once()

    def test_absent_without_unique_name_or_id_fails(self, mock_module, mock_client):
        """Test absent without unique_name or droplet_id fails"""
        mock_module.params["unique_name"] = False
        mock_module.params["droplet_id"] = None

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.state = "absent"
            droplet_obj.unique_name = False
            droplet_obj.droplet_id = None

            with pytest.raises(AnsibleFailJson) as exc:
                droplet_obj.absent()

            result = exc.value.args[0]
            assert result["failed"] is True
            assert "Must provide droplet_id" in result["msg"]


class TestDropletCreateDelete:
    """Test class for create and delete operations"""

    @patch("time.monotonic")
    @patch("time.sleep")
    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.get_droplet_by_id"
    )
    def test_create_droplet_success(
        self,
        mock_get_by_id,
        mock_sleep,
        mock_monotonic,
        mock_module,
        mock_client,
        sample_droplet,
    ):
        """Test successful droplet creation"""
        mock_monotonic.side_effect = [
            0,
            1,
        ]  # First call returns 0, second returns 1 (within timeout)
        sample_droplet["status"] = "active"
        mock_client.droplets.create.return_value = {"droplet": sample_droplet}
        mock_get_by_id.return_value = sample_droplet

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.timeout = 300
            droplet_obj.name = "test-droplet"
            droplet_obj.region = "nyc3"
            droplet_obj.size = "s-1vcpu-1gb"
            droplet_obj.image = "ubuntu-20-04-x64"
            droplet_obj.ssh_keys = []
            droplet_obj.backups = False
            droplet_obj.ipv6 = False
            droplet_obj.monitoring = False
            droplet_obj.tags = []
            droplet_obj.user_data = None
            droplet_obj.volumes = []
            droplet_obj.vpc_uuid = None
            droplet_obj.with_droplet_agent = False
            droplet_obj.module_override_options = None

            with pytest.raises(AnsibleExitJson) as exc:
                droplet_obj.create_droplet()

            result = exc.value.args[0]
            assert result["changed"] is True
            assert "Created Droplet" in result["msg"]

    @patch("time.monotonic")
    @patch("time.sleep")
    @patch(
        "ansible_collections.digitalocean.cloud.plugins.modules.droplet.Droplet.get_droplet_by_id"
    )
    def test_delete_droplet_success(
        self,
        mock_get_by_id,
        mock_sleep,
        mock_monotonic,
        mock_module,
        mock_client,
        sample_droplet,
    ):
        """Test successful droplet deletion"""
        mock_monotonic.side_effect = [0, 1]
        mock_get_by_id.return_value = None  # Droplet no longer exists after deletion

        with patch.object(
            droplet.DigitalOceanCommonModule, "__init__", return_value=None
        ):
            droplet_obj = droplet.Droplet.__new__(droplet.Droplet)
            droplet_obj.module = mock_module
            droplet_obj.client = mock_client
            droplet_obj.timeout = 300

            with pytest.raises(AnsibleExitJson) as exc:
                droplet_obj.delete_droplet(sample_droplet)

            result = exc.value.args[0]
            assert result["changed"] is True
            assert "Deleted Droplet" in result["msg"]
            mock_client.droplets.destroy.assert_called_once_with(droplet_id=123456)
