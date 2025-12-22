#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: reserved_ipv6

short_description: Create or delete reserved IPv6 addresses

version_added: 0.6.0

description:
  - Create or delete reserved IPv6 addresses.
  - |
    Reserved IPv6 addresses are static addresses that can be assigned to
    Droplets and retained across Droplet deletion and recreation.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Reserved-IPv6).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  region:
    description:
      - The slug identifier for the region where the reserved IPv6 will be created.
    type: str
    required: true
  ip:
    description:
      - The reserved IPv6 address.
      - Used for lookup when deleting.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create reserved IPv6
  digitalocean.cloud.reserved_ipv6:
    token: "{{ token }}"
    state: present
    region: nyc1

- name: Delete reserved IPv6
  digitalocean.cloud.reserved_ipv6:
    token: "{{ token }}"
    state: absent
    region: nyc1
    ip: "2604:a880:800:10::1"
"""


RETURN = r"""
reserved_ipv6:
  description: Reserved IPv6 information.
  returned: always
  type: dict
  sample:
    ip: "2604:a880:800:10::1"
    region_slug: nyc1
    reserved_at: '2020-03-13T19:20:47.442049222Z'
    droplet:
      id: 12345678
      name: my-droplet
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Reserved IPv6 result information.
  returned: always
  type: str
  sample:
    - Created reserved IPv6 2604:a880:800:10::1
    - Deleted reserved IPv6 2604:a880:800:10::1
    - Reserved IPv6 would be created
    - Reserved IPv6 2604:a880:800:10::1 does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class ReservedIPv6(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.region = module.params.get("region")
        self.ip = module.params.get("ip")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_reserved_ipv6(self):
        if not self.ip:
            return None
        try:
            reserved_ipv6s = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.reserved_ipv6,
                meth="list",
                key="reserved_ipv6s",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            for reserved_ipv6 in reserved_ipv6s:
                if self.ip == reserved_ipv6.get("ip"):
                    return reserved_ipv6
            return None
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
                reserved_ipv6={},
            )

    def create_reserved_ipv6(self):
        try:
            body = {
                "region": self.region,
            }
            reserved_ipv6 = self.client.reserved_ipv6.create(body=body)["reserved_ipv6"]

            self.module.exit_json(
                changed=True,
                msg=f"Created reserved IPv6 {reserved_ipv6['ip']}",
                reserved_ipv6=reserved_ipv6,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, reserved_ipv6={}
            )

    def delete_reserved_ipv6(self, reserved_ipv6):
        try:
            self.client.reserved_ipv6.delete(reserved_ip=reserved_ipv6["ip"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted reserved IPv6 {reserved_ipv6['ip']}",
                reserved_ipv6=reserved_ipv6,
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
                reserved_ipv6={},
            )

    def present(self):
        if self.ip:
            reserved_ipv6 = self.get_reserved_ipv6()
            if reserved_ipv6:
                self.module.exit_json(
                    changed=False,
                    msg=f"Reserved IPv6 {self.ip} exists",
                    reserved_ipv6=reserved_ipv6,
                )
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg="Reserved IPv6 would be created",
                reserved_ipv6={},
            )
        else:
            self.create_reserved_ipv6()

    def absent(self):
        if not self.ip:
            self.module.fail_json(
                changed=False,
                msg="ip is required when deleting a reserved IPv6",
                reserved_ipv6={},
            )
        reserved_ipv6 = self.get_reserved_ipv6()
        if reserved_ipv6 is None:
            self.module.exit_json(
                changed=False,
                msg=f"Reserved IPv6 {self.ip} does not exist",
                reserved_ipv6={},
            )
        else:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Reserved IPv6 {self.ip} would be deleted",
                    reserved_ipv6=reserved_ipv6,
                )
            else:
                self.delete_reserved_ipv6(reserved_ipv6=reserved_ipv6)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        region=dict(type="str", required=True),
        ip=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    ReservedIPv6(module)


if __name__ == "__main__":
    main()
