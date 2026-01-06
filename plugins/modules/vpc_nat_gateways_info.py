#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: vpc_nat_gateways_info

short_description: List all VPC NAT Gateways on your account

version_added: 1.9.0

description:
  - List all VPC NAT Gateways on your account.
  - |
    VPC NAT Gateways allow resources in a private VPC to access the public
    internet without exposing them to incoming traffic.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/vpc_nat_gateways_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get VPC NAT Gateways
  digitalocean.cloud.vpc_nat_gateways_info:
    token: "{{ token }}"
"""


RETURN = r"""
vpc_nat_gateways:
  description: VPC NAT Gateways.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      name: my-nat-gateway
      vpc_uuid: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      region: nyc1
      size: small
      created_at: '2020-03-13T19:20:47.442049222Z'
      status: ACTIVE
      public_ip: 192.0.2.1
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: VPC NAT Gateways result information.
  returned: always
  type: str
  sample:
    - Current VPC NAT Gateways
    - No VPC NAT Gateways
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class VPCNATGatewaysInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        vpc_nat_gateways = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.vpcnatgateways,
            meth="list",
            key="nat_gateways",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if vpc_nat_gateways:
            self.module.exit_json(
                changed=False,
                msg="Current VPC NAT Gateways",
                vpc_nat_gateways=vpc_nat_gateways,
            )
        self.module.exit_json(
            changed=False, msg="No VPC NAT Gateways", vpc_nat_gateways=[]
        )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    VPCNATGatewaysInformation(module)


if __name__ == "__main__":
    main()
