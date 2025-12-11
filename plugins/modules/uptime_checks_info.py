#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: uptime_checks_info

short_description: List all of the Uptime checks on your account

version_added: 0.5.0

description:
  - List all of the Uptime checks on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/uptime_list_checks).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.6
  - azure-core >= 1.26.1

options:
  state:
    description: Only C(present) is supported which will return the Uptime checks.
    type: str
    required: false
    default: present
    choices: [present]

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get Uptime checks
  digitalocean.cloud.uptime_checks_info:
    token: "{{ token }}"
"""


RETURN = r"""
checks:
  description: Uptime checks.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      name: Landing page check
      type: https
      target: https://www.landingpage.com
      regions:
        - us_east
        - eu_west
      enabled: true
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Uptime checks result information.
  returned: always
  type: str
  sample:
    - Current Uptime checks
    - No Uptime checks
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanFunctions,
    DigitalOceanOptions,
)


class UptimeChecksInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        checks = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.uptime,
            meth="list_checks",
            key="checks",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if checks:
            self.module.exit_json(
                changed=False,
                msg="Current Uptime checks",
                checks=checks,
            )
        self.module.exit_json(changed=False, msg="No Uptime checks", checks=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        state=dict(type="str", default="present", choices=["present"]),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    UptimeChecksInformation(module)


if __name__ == "__main__":
    main()
