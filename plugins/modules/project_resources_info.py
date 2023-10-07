#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: project_resources_info

short_description: Retrieve a list of all of the project resources in your account

version_added: 0.5.0

description:
  - Retrieve a list of all of the project resources in your account.
  - View the API documentation at (https://docs.digitalocean.com/reference/api/api-reference/#operation/projects_list_resources).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  project_id:
    description:
      - A unique identifier for a project.
      - If unspecified, return project resources from the default project.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get project resources
  digitalocean.cloud.project_resources_info:
    token: "{{ token }}"
"""


RETURN = r"""
project_resources:
  description: Project resources.
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
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Projects resources result information.
  returned: always
  type: str
  sample:
    - Current project resources
    - No project resources
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class ProjectResourcesInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.project_id = self.module.params.get("project_id")
        if self.state == "present":
            self.present()

    def get_by_project_id(self):
        """Returns project resources by project ID."""
        project_resources = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.projects,
            meth="list_resources",
            key="resources",
            exc=DigitalOceanCommonModule.HttpResponseError,
            project_id=self.project_id,
        )
        return project_resources

    def get_default(self):
        """Returns project resources from the default project."""
        try:
            project_resources = self.client.projects.list_resources_default()
            return project_resources["resources"]
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(changed=False, msg=error.get("Message"), error=error)

    def present(self):
        if not self.project_id:
            project_resources = self.get_default()
        else:
            project_resources = self.get_by_project_id()

        if len(project_resources):
            self.module.exit_json(
                changed=False,
                msg="Current project resources",
                project_resources=project_resources,
            )
        self.module.exit_json(
            changed=False, msg="No project resources", project_resources=[]
        )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        project_id=dict(type="str", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    ProjectResourcesInformation(module)


if __name__ == "__main__":
    main()
