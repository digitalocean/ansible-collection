#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: projects_info

short_description: Retrieve a list of all of the projects in your account

version_added: 0.2.0

description:
  - Retrieve a list of all of the projects in your account.
  - View the API documentation at (https://docs.digitalocean.com/reference/api/api-reference/#operation/projects_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get projects
  digitalocean.cloud.projects_info:
    token: "{{ token }}"
"""


RETURN = r"""
projects:
  description: Projects.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 4e1bfbc3-dc3e-41f2-a18f-1b4d7ba71679
      owner_uuid: 99525febec065ca37b2ffe4f852fd2b2581895e7
      owner_id: 258992
      name: my-web-api
      description: My website API
      purpose: Service or API
      environment: Production
      is_default: false
      created_at: '2018-09-27T20:10:35Z'
      updated_at: '2018-09-27T20:10:35Z'
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Projects result information.
  returned: always
  type: str
  sample:
    - Current projects
    - No projects
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class ProjectsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        try:
            projects = self.client.projects.list()
            if projects:
                self.module.exit_json(
                    changed=False, msg="Current projects", projects=projects
                )
            self.module.exit_json(changed=False, msg="No projects", projects=[])
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(changed=False, msg=error.get("Message"), error=error)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    ProjectsInformation(module)


if __name__ == "__main__":
    main()
