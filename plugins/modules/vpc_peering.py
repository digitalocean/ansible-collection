#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: vpc_peering

short_description: Create or delete VPC Peerings

version_added: 1.9.0

description:
  - Create or delete VPC Peerings.
  - |
    VPC Peerings join two VPC networks with a secure, private connection.
    This allows resources in those networks to connect to each other's private
    IP addresses as if they were in the same network.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/VPC-Peerings).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The name of the VPC Peering. Must be unique and may only contain alphanumeric characters, dashes, and periods.
    type: str
    required: true
  vpc_ids:
    description:
      - An array of two VPC IDs that the peering will connect.
      - Required when creating a new VPC Peering.
    type: list
    elements: str
    required: false
  id:
    description:
      - The unique identifier of the VPC Peering.
      - Used for lookup when deleting or updating.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create VPC Peering
  digitalocean.cloud.vpc_peering:
    token: "{{ token }}"
    state: present
    name: my-vpc-peering
    vpc_ids:
      - 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      - 9a4981aa-9653-4bd1-bef5-d6bff52042e5

- name: Delete VPC Peering by name
  digitalocean.cloud.vpc_peering:
    token: "{{ token }}"
    state: absent
    name: my-vpc-peering

- name: Delete VPC Peering by ID
  digitalocean.cloud.vpc_peering:
    token: "{{ token }}"
    state: absent
    name: my-vpc-peering
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
"""


RETURN = r"""
vpc_peering:
  description: VPC Peering information.
  returned: always
  type: dict
  sample:
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
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
  description: VPC Peering result information.
  returned: always
  type: str
  sample:
    - Created VPC Peering my-vpc-peering (5a4981aa-9653-4bd1-bef5-d6bff52042e4)
    - Deleted VPC Peering my-vpc-peering (5a4981aa-9653-4bd1-bef5-d6bff52042e4)
    - VPC Peering my-vpc-peering would be created
    - VPC Peering my-vpc-peering (5a4981aa-9653-4bd1-bef5-d6bff52042e4) exists
    - VPC Peering my-vpc-peering does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class VPCPeering(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.vpc_ids = module.params.get("vpc_ids")
        self.id = module.params.get("id")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_vpc_peerings(self):
        try:
            vpc_peerings = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.vpc_peerings,
                meth="list",
                key="vpc_peerings",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            found_vpc_peerings = []
            for vpc_peering in vpc_peerings:
                if self.name == vpc_peering.get("name"):
                    found_vpc_peerings.append(vpc_peering)
                elif self.id and self.id == vpc_peering.get("id"):
                    found_vpc_peerings.append(vpc_peering)
            return found_vpc_peerings
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
                vpc_peering=[],
            )

    def create_vpc_peering(self):
        try:
            body = {
                "name": self.name,
                "vpc_ids": self.vpc_ids,
            }
            vpc_peering = self.client.vpc_peerings.create(body=body)["vpc_peering"]

            self.module.exit_json(
                changed=True,
                msg=f"Created VPC Peering {self.name} ({vpc_peering['id']})",
                vpc_peering=vpc_peering,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, vpc_peering=[]
            )

    def delete_vpc_peering(self, vpc_peering):
        try:
            self.client.vpc_peerings.delete(vpc_peering_id=vpc_peering["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted VPC Peering {self.name} ({vpc_peering['id']})",
                vpc_peering=vpc_peering,
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
                vpc_peering=[],
            )

    def present(self):
        vpc_peerings = self.get_vpc_peerings()
        if len(vpc_peerings) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"VPC Peering {self.name} would be created",
                    vpc_peering=[],
                )
            else:
                if not self.vpc_ids:
                    self.module.fail_json(
                        changed=False,
                        msg="vpc_ids is required when creating a VPC Peering",
                        vpc_peering=[],
                    )
                self.create_vpc_peering()
        elif len(vpc_peerings) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"VPC Peering {self.name} ({vpc_peerings[0]['id']}) exists",
                vpc_peering=vpc_peerings[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(vpc_peerings)} VPC Peerings named {self.name}",
                vpc_peering=[],
            )

    def absent(self):
        vpc_peerings = self.get_vpc_peerings()
        if len(vpc_peerings) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"VPC Peering {self.name} does not exist",
                vpc_peering=[],
            )
        elif len(vpc_peerings) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"VPC Peering {self.name} ({vpc_peerings[0]['id']}) would be deleted",
                    vpc_peering=vpc_peerings[0],
                )
            else:
                self.delete_vpc_peering(vpc_peering=vpc_peerings[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(vpc_peerings)} VPC Peerings named {self.name}",
                vpc_peering=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        vpc_ids=dict(type="list", elements="str", required=False),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    VPCPeering(module)


if __name__ == "__main__":
    main()
