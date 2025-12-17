# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
from unittest.mock import MagicMock, patch
from ansible.inventory.data import InventoryData
from ansible.template import Templar


# Mock the common module to avoid import errors
class MockDigitalOceanCommonInventory:
    def __init__(self, config):
        self.client = MagicMock()
        self.client.droplets = MagicMock()


@pytest.fixture
def mock_imports():
    """Mock the ansible_collections imports that aren't available in test environment."""
    with patch.dict(
        "sys.modules",
        {
            "ansible_collections.digitalocean.cloud.plugins.module_utils.common": MagicMock(
                DigitalOceanCommonInventory=MockDigitalOceanCommonInventory,
                DigitalOceanFunctions=MagicMock(),
            ),
        },
    ):
        yield


@pytest.fixture
def inventory_plugin(mock_imports):
    """Create an instance of the inventory plugin for testing."""
    from plugins.inventory.droplets import InventoryModule

    plugin = InventoryModule()
    plugin.inventory = InventoryData()
    plugin.templar = Templar(loader=None)
    plugin.display = MagicMock()
    plugin.config = {
        "token": "test-token",
        "attributes": ["id", "name", "region", "tags", "status"],
    }

    # Mock get_option
    def mock_get_option(option):
        options = {
            "strict": False,
            "filters": [],
            "api_filters": {},
            "cache": False,
            "compose": {},
            "groups": {},
            "keyed_groups": [],
            "attributes": ["id", "name", "region", "tags", "status"],
        }
        return options.get(option)

    plugin.get_option = mock_get_option
    return plugin


class TestDropletsInventoryPlugin:
    """Test the droplets inventory plugin."""

    def test_passes_filters_no_filters(self, inventory_plugin):
        """Test that hosts pass when no filters are defined."""
        result = inventory_plugin._passes_filters(None, {}, "test-host")
        assert result is True

        result = inventory_plugin._passes_filters([], {}, "test-host")
        assert result is True

    def test_passes_filters_with_matching_tag(self, inventory_plugin):
        """Test filter matching with tags."""
        variables = {"do_tags": ["web", "production"]}

        # Mock _compose to return True for matching filter
        with patch.object(inventory_plugin, "_compose", return_value=True):
            result = inventory_plugin._passes_filters(
                ['"web" in do_tags'], variables, "test-host"
            )
            assert result is True

    def test_passes_filters_with_non_matching_tag(self, inventory_plugin):
        """Test filter not matching with tags."""
        variables = {"do_tags": ["database", "staging"]}

        # Mock _compose to return False for non-matching filter
        with patch.object(inventory_plugin, "_compose", return_value=False):
            result = inventory_plugin._passes_filters(
                ['"web" in do_tags'], variables, "test-host"
            )
            assert result is False

    def test_passes_filters_multiple_conditions(self, inventory_plugin):
        """Test multiple filter conditions (AND logic)."""
        variables = {
            "do_tags": ["web", "production"],
            "region": {"slug": "nyc3", "name": "New York 3"},
            "status": "active",
        }

        # Mock _compose to return True for all filters
        with patch.object(inventory_plugin, "_compose", return_value=True):
            result = inventory_plugin._passes_filters(
                ['"web" in do_tags', 'region.slug == "nyc3"', 'status == "active"'],
                variables,
                "test-host",
            )
            assert result is True

    def test_passes_filters_one_fails(self, inventory_plugin):
        """Test that if one filter fails, the host is excluded."""
        variables = {
            "do_tags": ["web"],
            "region": {"slug": "nyc3"},
            "status": "off",
        }

        call_count = [0]

        def mock_compose(template, vars):
            call_count[0] += 1
            # First filter passes, second fails
            if call_count[0] == 1:
                return True
            return False

        with patch.object(inventory_plugin, "_compose", side_effect=mock_compose):
            result = inventory_plugin._passes_filters(
                ['"web" in do_tags', 'status == "active"'], variables, "test-host"
            )
            assert result is False

    def test_passes_filters_exception_handling(self, inventory_plugin):
        """Test that filter exceptions are handled gracefully."""
        variables = {"do_tags": ["web"]}

        # Mock _compose to raise an exception
        with patch.object(
            inventory_plugin,
            "_compose",
            side_effect=Exception("Template error"),
        ):
            result = inventory_plugin._passes_filters(
                ['"web" in do_tags'], variables, "test-host", strict=False
            )
            assert result is False

    def test_passes_filters_strict_mode(self, inventory_plugin):
        """Test that strict mode raises exceptions."""
        variables = {"do_tags": ["web"]}

        # Mock _compose to raise an exception
        with patch.object(
            inventory_plugin,
            "_compose",
            side_effect=Exception("Template error"),
        ):
            with pytest.raises(Exception):
                inventory_plugin._passes_filters(
                    ['"web" in do_tags'], variables, "test-host", strict=True
                )
