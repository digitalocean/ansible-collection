#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: project_resource

short_description: Assign or remove resources from a project

version_added: 1.9.0

description:
  - Assign or remove resources from a project.
  - |
    Projects allow you to organize your resources into groups that fit the
    way you work.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Project-Resources).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  project_id:
    description:
      - The UUID of the project.
    type: str
    required: true
  resources:
    description:
      - An array of uniform resource names (URNs) to assign to the project.
      - |
        Resource URNs have the format: do:resource_type:resource_id
        Examples: do:droplet:12345, do:kubernetes:cluster-uuid
    type: list
    elements: str
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Assign resources to project
  digitalocean.cloud.project_resource:
    token: "{{ token }}"
    state: present
    project_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    resources:
      - do:droplet:12345678
      - do:volume:87654321

- name: Remove resources from project (moves to default project)
  digitalocean.cloud.project_resource:
    token: "{{ token }}"
    state: absent
    project_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    resources:
      - do:droplet:12345678
"""


RETURN = r"""
resources:
  description: Resources assigned to the project.
  returned: always
  type: list
  elements: dict
  sample:
    - urn: do:droplet:12345678
      assigned_at: '2020-03-13T19:20:47Z'
      links:
        self: https://api.digitalocean.com/v2/droplets/12345678
      status: ok
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Project resource result information.
  returned: always
  type: str
  sample:
    - Assigned resources to project
    - Resources would be assigned to project
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class ProjectResource(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.project_id = module.params.get("project_id")
        self.resources = module.params.get("resources")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def assign_resources(self):
        try:
            body = {
                "resources": self.resources,
            }
            result = self.client.projects.assign_resources(
                project_id=self.project_id, body=body
            )
            resources = result.get("resources", [])

            self.module.exit_json(
                changed=True,
                msg="Assigned resources to project",
                resources=resources,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, resources=[]
            )

    def get_default_project_id(self):
        try:
            # Get default project
            result = self.client.projects.get_default()
            return result.get("project", {}).get("id")
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, resources=[]
            )

    def remove_resources(self):
        try:
            # To remove resources, we assign them to the default project
            default_project_id = self.get_default_project_id()
            if not default_project_id:
                self.module.fail_json(
                    changed=False,
                    msg="Could not find default project",
                    resources=[],
                )

            body = {
                "resources": self.resources,
            }
            result = self.client.projects.assign_resources(
                project_id=default_project_id, body=body
            )
            resources = result.get("resources", [])

            self.module.exit_json(
                changed=True,
                msg="Moved resources to default project",
                resources=resources,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, resources=[]
            )

    def present(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg="Resources would be assigned to project",
                resources=[],
            )
        else:
            self.assign_resources()

    def absent(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg="Resources would be moved to default project",
                resources=[],
            )
        else:
            self.remove_resources()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        project_id=dict(type="str", required=True),
        resources=dict(type="list", elements="str", required=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    ProjectResource(module)


if __name__ == "__main__":
    main()
