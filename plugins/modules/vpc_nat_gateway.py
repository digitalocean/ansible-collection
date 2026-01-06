#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: vpc_nat_gateway

short_description: Create or delete VPC NAT Gateways

version_added: 1.9.0

description:
  - Create or delete VPC NAT Gateways.
  - |
    VPC NAT Gateways allow resources in a private VPC to access the public
    internet without exposing them to incoming traffic.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/VPC-NAT-Gateways).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The name of the VPC NAT Gateway.
      - Must be unique and may only contain alphanumeric characters, dashes, and periods.
    type: str
    required: true
  vpc_uuid:
    description:
      - The UUID of the VPC to create the NAT Gateway in.
      - Required when creating a new NAT Gateway.
    type: str
    required: false
  region:
    description:
      - The slug identifier for the region where the NAT Gateway will be created.
    type: str
    required: false
  size:
    description:
      - The size of the NAT Gateway.
    type: str
    required: false
    choices:
      - small
      - medium
      - large
  id:
    description:
      - The unique identifier of the VPC NAT Gateway.
      - Used for lookup when deleting or updating.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create VPC NAT Gateway
  digitalocean.cloud.vpc_nat_gateway:
    token: "{{ token }}"
    state: present
    name: my-nat-gateway
    vpc_uuid: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    region: nyc1
    size: small

- name: Delete VPC NAT Gateway by name
  digitalocean.cloud.vpc_nat_gateway:
    token: "{{ token }}"
    state: absent
    name: my-nat-gateway

- name: Delete VPC NAT Gateway by ID
  digitalocean.cloud.vpc_nat_gateway:
    token: "{{ token }}"
    state: absent
    name: my-nat-gateway
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
"""


RETURN = r"""
vpc_nat_gateway:
  description: VPC NAT Gateway information.
  returned: always
  type: dict
  sample:
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
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
  description: VPC NAT Gateway result information.
  returned: always
  type: str
  sample:
    - Created VPC NAT Gateway my-nat-gateway (5a4981aa-9653-4bd1-bef5-d6bff52042e4)
    - Deleted VPC NAT Gateway my-nat-gateway (5a4981aa-9653-4bd1-bef5-d6bff52042e4)
    - VPC NAT Gateway my-nat-gateway would be created
    - VPC NAT Gateway my-nat-gateway (5a4981aa-9653-4bd1-bef5-d6bff52042e4) exists
    - VPC NAT Gateway my-nat-gateway does not exist
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
    DigitalOceanConstants,
)


class VPCNATGateway(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.vpc_uuid = module.params.get("vpc_uuid")
        self.region = module.params.get("region")
        self.size = module.params.get("size")
        self.id = module.params.get("id")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_vpc_nat_gateways(self):
        try:
            vpc_nat_gateways = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.vpcnatgateways,
                meth="list",
                key="nat_gateways",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            found_vpc_nat_gateways = []
            for vpc_nat_gateway in vpc_nat_gateways:
                if self.name == vpc_nat_gateway.get("name"):
                    found_vpc_nat_gateways.append(vpc_nat_gateway)
                elif self.id and self.id == vpc_nat_gateway.get("id"):
                    found_vpc_nat_gateways.append(vpc_nat_gateway)
            return found_vpc_nat_gateways
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
                vpc_nat_gateway=[],
            )

    def create_vpc_nat_gateway(self):
        try:
            body = {
                "name": self.name,
                "vpc_uuid": self.vpc_uuid,
            }
            if self.region:
                body["region"] = self.region
            if self.size:
                body["size"] = self.size

            vpc_nat_gateway = self.client.vpcnatgateways.create(body=body)[
                "nat_gateway"
            ]

            # Wait for the NAT Gateway to become active
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                status = vpc_nat_gateway.get("status", "").upper()
                if status == "ACTIVE":
                    break
                time.sleep(DigitalOceanConstants.SLEEP)
                try:
                    vpc_nat_gateway = self.client.vpcnatgateways.get(
                        id=vpc_nat_gateway["id"]
                    )["nat_gateway"]
                except DigitalOceanCommonModule.HttpResponseError:
                    pass

            self.module.exit_json(
                changed=True,
                msg=f"Created VPC NAT Gateway {self.name} ({vpc_nat_gateway['id']})",
                vpc_nat_gateway=vpc_nat_gateway,
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
                vpc_nat_gateway=[],
            )

    def delete_vpc_nat_gateway(self, vpc_nat_gateway):
        try:
            self.client.vpcnatgateways.delete(id=vpc_nat_gateway["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted VPC NAT Gateway {self.name} ({vpc_nat_gateway['id']})",
                vpc_nat_gateway=vpc_nat_gateway,
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
                vpc_nat_gateway=[],
            )

    def present(self):
        vpc_nat_gateways = self.get_vpc_nat_gateways()
        if len(vpc_nat_gateways) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"VPC NAT Gateway {self.name} would be created",
                    vpc_nat_gateway=[],
                )
            else:
                if not self.vpc_uuid:
                    self.module.fail_json(
                        changed=False,
                        msg="vpc_uuid is required when creating a VPC NAT Gateway",
                        vpc_nat_gateway=[],
                    )
                self.create_vpc_nat_gateway()
        elif len(vpc_nat_gateways) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"VPC NAT Gateway {self.name} ({vpc_nat_gateways[0]['id']}) exists",
                vpc_nat_gateway=vpc_nat_gateways[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(vpc_nat_gateways)} VPC NAT Gateways named {self.name}",
                vpc_nat_gateway=[],
            )

    def absent(self):
        vpc_nat_gateways = self.get_vpc_nat_gateways()
        if len(vpc_nat_gateways) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"VPC NAT Gateway {self.name} does not exist",
                vpc_nat_gateway=[],
            )
        elif len(vpc_nat_gateways) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"VPC NAT Gateway {self.name} ({vpc_nat_gateways[0]['id']}) would be deleted",
                    vpc_nat_gateway=vpc_nat_gateways[0],
                )
            else:
                self.delete_vpc_nat_gateway(vpc_nat_gateway=vpc_nat_gateways[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(vpc_nat_gateways)} VPC NAT Gateways named {self.name}",
                vpc_nat_gateway=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        vpc_uuid=dict(type="str", required=False),
        region=dict(type="str", required=False),
        size=dict(type="str", required=False, choices=["small", "medium", "large"]),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    VPCNATGateway(module)


if __name__ == "__main__":
    main()
