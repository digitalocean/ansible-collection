#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: vpcs_info

short_description: List all of the VPCs on your account

version_added: 0.2.0

description:
  - List all of the VPCs on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/vpcs_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get VPCs
  digitalocean.cloud.vpcs_info:
    token: "{{ token }}"
"""


RETURN = r"""
vpcs:
  description: VPCs.
  returned: always
  type: list
  elements: dict
  sample:
    - created_at: '2021-11-05T21:48:35Z'
      default: true
      description: ''
      id: 30f86d25-414e-434f-852d-993ed8d6815e
      ip_range: 10.108.0.0/20
      name: default-nyc3
      region: nyc3
      urn: do:vpc:30f86d25-414e-434f-852d-993ed8d6815e
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: VPCs kresult information.
  returned: always
  type: str
  sample:
    - Current volumes
    - No volumes
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class VPCsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        vpcs = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.vpcs,
            meth="list",
            key="vpcs",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if vpcs:
            self.module.exit_json(
                changed=False,
                msg="Current VPCs",
                vpcs=vpcs,
            )
        self.module.exit_json(changed=False, msg="No VPCs", vpcs=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    VPCsInformation(module)


if __name__ == "__main__":
    main()
