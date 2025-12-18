#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: project_resources

short_description: Assign resources to a project

version_added: 1.8.0

description:
  - Assign resources to a DigitalOcean project.
  - |
    Resources can be assigned using their URN (Uniform Resource Name) in the format
    C(do:resource_type:resource_id), for example C(do:droplet:13457723).
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/projects_assign_resources).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  project_id:
    description:
      - A unique identifier for the project.
      - Either C(project_id) or C(project_name) must be specified.
      - If both are specified, C(project_id) takes precedence.
    type: str
    required: false
  project_name:
    description:
      - The name of the project.
      - Either C(project_id) or C(project_name) must be specified.
      - If both are specified, C(project_id) takes precedence.
    type: str
    required: false
  resources:
    description:
      - A list of resource URNs to assign to the project.
      - |
        Each URN should be in the format C(do:resource_type:resource_id), for example
        C(do:droplet:13457723), C(do:volume:6fc4c277-ea5c-448a-93cd-dd496cfef71f),
        C(do:floatingip:192.0.2.1), C(do:domain:example.com), C(do:loadbalancer:4de7ac8b-495b-4884-9a69-1050c6793cd6).
      - Resource types supported include droplets, volumes, floating IPs, domains, and load balancers.
      - Required when C(state=present).
    type: list
    elements: str
    required: false
    default: []

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Assign resources to a project by project ID
  digitalocean.cloud.project_resources:
    token: "{{ token }}"
    state: present
    project_id: "4e1bfbc3-dc3e-41f2-a18f-1b4d7ba71679"
    resources:
      - "do:droplet:13457723"
      - "do:volume:6fc4c277-ea5c-448a-93cd-dd496cfef71f"
      - "do:floatingip:192.0.2.1"

- name: Assign resources to a project by project name
  digitalocean.cloud.project_resources:
    token: "{{ token }}"
    state: present
    project_name: "my-web-api"
    resources:
      - "do:droplet:13457723"
      - "do:domain:example.com"

- name: Assign a Droplet to the default project
  digitalocean.cloud.project_resources:
    token: "{{ token }}"
    state: present
    project_name: "default"
    resources:
      - "do:droplet:13457723"
"""


RETURN = r"""
project:
  description: Project information.
  returned: always
  type: dict
  sample:
    id: 4e1bfbc3-dc3e-41f2-a18f-1b4d7ba71679
    owner_uuid: 99525febec065ca37b2ffe4f852fd2b2581895e7
    owner_id: 258992
    name: my-web-api
    description: My website API
    purpose: Service or API
    environment: Production
    created_at: '2018-09-27T20:10:35Z'
    updated_at: '2018-09-27T20:10:35Z'
    is_default: false
resources:
  description: Resources assigned to the project.
  returned: always
  type: list
  elements: dict
  sample:
    - urn: do:droplet:13457723
      assigned_at: "2018-09-28T19:26:37Z"
      links:
        self: "https://api.digitalocean.com/v2/droplets/13457723"
      status: ok
    - urn: "do:domain:example.com"
      assigned_at: "2019-03-31T16:24:14Z"
      links:
        self: "https://api.digitalocean.com/v2/domains/example.com"
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
  description: Project resources result information.
  returned: always
  type: str
  sample:
    - Assigned 3 resource(s) to project my-web-api (4e1bfbc3-dc3e-41f2-a18f-1b4d7ba71679)
    - 3 resource(s) would be assigned to project my-web-api (4e1bfbc3-dc3e-41f2-a18f-1b4d7ba71679)
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class ProjectResources(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.project_id = module.params.get("project_id")
        self.project_name = module.params.get("project_name")
        self.resources = module.params.get("resources")

        if self.state == "present":
            self.present()

    def get_project_by_name(self, name):
        """Get a project by name."""
        try:
            projects = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.projects,
                meth="list",
                key="projects",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            found_projects = []
            for project in projects:
                if project["name"] == name:
                    found_projects.append(project)

            if len(found_projects) == 0:
                self.module.fail_json(
                    changed=False,
                    msg=f"No project named {name}",
                    project={},
                    resources=[],
                )
            elif len(found_projects) > 1:
                project_ids = ", ".join([p["id"] for p in found_projects])
                self.module.fail_json(
                    changed=False,
                    msg=f"There are currently {len(found_projects)} projects named {name}: {project_ids}",
                    project={},
                    resources=[],
                )
            return found_projects[0]
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                project={},
                resources=[],
            )

    def get_project_by_id(self, project_id):
        """Get a project by ID."""
        try:
            project = self.client.projects.get(project_id=project_id)["project"]
            return project
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                project={},
                resources=[],
            )

    def get_project(self):
        """Get the project based on project_id or project_name."""
        if self.project_id:
            return self.get_project_by_id(self.project_id)
        elif self.project_name:
            return self.get_project_by_name(self.project_name)
        else:
            self.module.fail_json(
                changed=False,
                msg="Either project_id or project_name must be specified",
                project={},
                resources=[],
            )

    def assign_resources(self, project):
        """Assign resources to a project."""
        try:
            body = {
                "resources": self.resources,
            }
            result = self.client.projects.assign_resources(
                project_id=project["id"], body=body
            )
            resources = result.get("resources", [])

            self.module.exit_json(
                changed=True,
                msg=f"Assigned {len(self.resources)} resource(s) to project {project['name']} ({project['id']})",
                project=project,
                resources=resources,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                project=project,
                resources=[],
            )

    def present(self):
        if not self.resources:
            self.module.fail_json(
                changed=False,
                msg="resources parameter is required when state is present",
                project={},
                resources=[],
            )

        project = self.get_project()

        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"{len(self.resources)} resource(s) would be assigned to project {project['name']} ({project['id']})",
                project=project,
                resources=[],
            )
        else:
            self.assign_resources(project)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        project_id=dict(type="str", required=False),
        project_name=dict(type="str", required=False),
        resources=dict(type="list", elements="str", required=False, default=[]),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[
            ("project_id", "project_name"),
        ],
        required_if=[
            ("state", "present", ("resources",)),
        ],
    )
    ProjectResources(module)


if __name__ == "__main__":
    main()
