# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import pytest
import sys
from unittest.mock import MagicMock
from ansible.module_utils import basic
from ansible.module_utils.common.text.converters import to_bytes
import json

# Mock dependencies before importing the module
sys.modules["pydo"] = MagicMock()
sys.modules["azure"] = MagicMock()
sys.modules["azure.core"] = MagicMock()
sys.modules["azure.core.exceptions"] = MagicMock()

# Import the module after mocking dependencies
from ansible_collections.digitalocean.cloud.plugins.modules import project_resources


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
    args = args or {}
    args["_ansible_remote_tmp"] = "/tmp"
    args["_ansible_keep_remote_files"] = False

    default_args = {
        "token": "test-token",
    }
    default_args.update(args)

    basic._ANSIBLE_ARGS = to_bytes(json.dumps({"ANSIBLE_MODULE_ARGS": default_args}))
    # Set the serialization profile for newer Ansible versions
    basic._ANSIBLE_PROFILE = "json"


@pytest.fixture(autouse=True)
def patch_exit_fail(monkeypatch):
    monkeypatch.setattr(basic.AnsibleModule, "exit_json", exit_json)
    monkeypatch.setattr(basic.AnsibleModule, "fail_json", fail_json)

    # Patch _load_params to work around serialization issues in newer Ansible
    def mock_load_params():
        import json

        if basic._ANSIBLE_ARGS is not None:
            data = json.loads(basic._ANSIBLE_ARGS.decode("utf-8"))
            return data.get("ANSIBLE_MODULE_ARGS", {})
        return {}

    monkeypatch.setattr("ansible.module_utils.basic._load_params", mock_load_params)


@pytest.fixture(autouse=True)
def patch_dependencies(monkeypatch):
    # Dependencies are already mocked at module level
    # This fixture is kept for consistency but doesn't need to do anything
    pass


def test_missing_required_one_of():
    set_module_args({"state": "present", "resources": ["do:droplet:1"]})
    # Should fail due to missing both project_id and project_name
    with pytest.raises(AnsibleFailJson) as exc:
        project_resources.main()
    result = exc.value.args[0]
    assert result["failed"] is True
    assert "project_id" in result["msg"] and "project_name" in result["msg"]


def test_present_requires_resources():
    set_module_args({"state": "present", "project_id": "pid", "resources": []})
    with pytest.raises(AnsibleFailJson) as exc:
        project_resources.main()
    result = exc.value.args[0]
    assert result["failed"] is True
    assert "resources" in result["msg"]


def test_check_mode_assigns_no_resources(monkeypatch):
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
