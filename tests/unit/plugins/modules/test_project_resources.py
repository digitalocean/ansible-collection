# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
import sys
from unittest.mock import MagicMock, patch
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
import json


# Custom exceptions to capture exit_json/fail_json
class AnsibleExitJson(Exception):
    pass


class AnsibleFailJson(Exception):
    pass


def exit_json(*args, **kwargs):
    if "changed" not in kwargs:
        kwargs["changed"] = False
    raise AnsibleExitJson(kwargs)


def fail_json(*args, **kwargs):
    kwargs["failed"] = True
    raise AnsibleFailJson(kwargs)


def set_module_args(args):
    args = json.dumps({"ANSIBLE_MODULE_ARGS": args})
    basic._ANSIBLE_ARGS = to_bytes(args)


@pytest.fixture(autouse=True)
def patch_exit_fail(monkeypatch):
    monkeypatch.setattr(basic, "exit_json", exit_json)
    monkeypatch.setattr(basic, "fail_json", fail_json)


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # Patch DigitalOceanCommonModule and dependencies
    sys.modules["pydo"] = MagicMock()
    sys.modules["azure"] = MagicMock()
    sys.modules["azure.core"] = MagicMock()
    sys.modules["azure.core.exceptions"] = MagicMock()
    monkeypatch.setattr(
        "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanCommonModule",
        MagicMock(),
    )
    monkeypatch.setattr(
        "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanOptions",
        MagicMock(),
    )
    monkeypatch.setattr(
        "ansible_collections.digitalocean.cloud.plugins.module_utils.common.DigitalOceanFunctions",
        MagicMock(),
    )


def test_missing_required_one_of():
    from ansible_collections.digitalocean.cloud.plugins.modules import project_resources

    set_module_args({"state": "present", "resources": ["do:droplet:1"]})
    # Should fail due to missing both project_id and project_name
    with pytest.raises(AnsibleFailJson) as exc:
        project_resources.main()
    result = exc.value.args[0]
    assert result["failed"] is True
    assert "project_id or project_name" in result["msg"]


def test_present_requires_resources():
    from ansible_collections.digitalocean.cloud.plugins.modules import project_resources

    set_module_args({"state": "present", "project_id": "pid", "resources": []})
    with pytest.raises(AnsibleFailJson) as exc:
        project_resources.main()
    result = exc.value.args[0]
    assert result["failed"] is True
    assert "resources parameter is required" in result["msg"]


def test_check_mode_assigns_no_resources(monkeypatch):
    from ansible_collections.digitalocean.cloud.plugins.modules import project_resources

    # Patch ProjectResources.get_project to return a fake project
    monkeypatch.setattr(
        project_resources.ProjectResources,
        "get_project",
        lambda self: {"id": "pid", "name": "test"},
    )
    set_module_args(
        {"state": "present", "project_id": "pid", "resources": ["do:droplet:1"]}
    )

    # Patch check_mode to True
    def fake_init(self, module):
        self.module = module
        self.state = "present"
        self.project_id = "pid"
        self.project_name = None
        self.resources = ["do:droplet:1"]
        self.module.check_mode = True
        self.present()

    monkeypatch.setattr(project_resources.ProjectResources, "__init__", fake_init)
    with pytest.raises(AnsibleExitJson) as exc:
        project_resources.main()
    result = exc.value.args[0]
    assert result["changed"] is True
    assert "would be assigned" in result["msg"]


def test_assign_resources_calls_assign(monkeypatch):
    from ansible_collections.digitalocean.cloud.plugins.modules import project_resources

    # Patch ProjectResources.get_project and assign_resources
    monkeypatch.setattr(
        project_resources.ProjectResources,
        "get_project",
        lambda self: {"id": "pid", "name": "test"},
    )
    called = {}

    def fake_assign(self, project):
        called["assign"] = True
        # Simulate exit_json
        self.module.exit_json(
            changed=True,
            msg="Assigned",
            project=project,
            resources=[{"urn": "do:droplet:1"}],
        )

    monkeypatch.setattr(
        project_resources.ProjectResources, "assign_resources", fake_assign
    )

    def fake_init(self, module):
        self.module = module
        self.state = "present"
        self.project_id = "pid"
        self.project_name = None
        self.resources = ["do:droplet:1"]
        self.module.check_mode = False
        self.present()

    monkeypatch.setattr(project_resources.ProjectResources, "__init__", fake_init)
    set_module_args(
        {"state": "present", "project_id": "pid", "resources": ["do:droplet:1"]}
    )
    with pytest.raises(AnsibleExitJson) as exc:
        project_resources.main()
    result = exc.value.args[0]
    assert result["changed"] is True
    assert result["msg"] == "Assigned"
    assert called["assign"] is True
