#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: vpc_peerings_info

short_description: List all VPC Peerings on your account

version_added: 0.6.0

description:
  - List all VPC Peerings on your account.
  - |
    VPC Peerings join two VPC networks with a secure, private connection.
    This allows resources in those networks to connect to each other's private
    IP addresses as if they were in the same network.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/vpc_peerings_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get VPC Peerings
  digitalocean.cloud.vpc_peerings_info:
    token: "{{ token }}"
"""


RETURN = r"""
vpc_peerings:
  description: VPC Peerings.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      name: my-vpc-peering
      vpc_ids:
        - 5a4981aa-9653-4bd1-bef5-d6bff52042e4
        - 9a4981aa-9653-4bd1-bef5-d6bff52042e5
      created_at: '2020-03-13T19:20:47.442049222Z'
      status: ACTIVE
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: VPC Peerings result information.
  returned: always
  type: str
  sample:
    - Current VPC Peerings
    - No VPC Peerings
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class VPCPeeringsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        vpc_peerings = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.vpc_peerings,
            meth="list",
            key="vpc_peerings",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if vpc_peerings:
            self.module.exit_json(
                changed=False,
                msg="Current VPC Peerings",
                vpc_peerings=vpc_peerings,
            )
        self.module.exit_json(changed=False, msg="No VPC Peerings", vpc_peerings=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    VPCPeeringsInformation(module)


if __name__ == "__main__":
    main()
