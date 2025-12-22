#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: floating_ip

short_description: Create or delete floating IPs (legacy)

version_added: 0.6.0

description:
  - Create or delete floating IPs.
  - |
    NOTE: Floating IPs have been renamed to Reserved IPs. This module is
    provided for backwards compatibility. New implementations should use
    the reserved_ip module instead.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Floating-IPs).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  region:
    description:
      - The slug identifier for the region where the floating IP will be reserved.
      - Required when creating a floating IP without a droplet_id.
    type: str
    required: false
  droplet_id:
    description:
      - The ID of the Droplet that the floating IP will be assigned to.
    type: int
    required: false
  ip:
    description:
      - The floating IP address.
      - Used for lookup when deleting.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create floating IP in region
  digitalocean.cloud.floating_ip:
    token: "{{ token }}"
    state: present
    region: nyc1

- name: Create floating IP and assign to Droplet
  digitalocean.cloud.floating_ip:
    token: "{{ token }}"
    state: present
    droplet_id: 12345678

- name: Delete floating IP
  digitalocean.cloud.floating_ip:
    token: "{{ token }}"
    state: absent
    ip: 192.0.2.1
"""


RETURN = r"""
floating_ip:
  description: Floating IP information.
  returned: always
  type: dict
  sample:
    ip: 192.0.2.1
    region:
      name: New York 1
      slug: nyc1
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
  description: Floating IP result information.
  returned: always
  type: str
  sample:
    - Created floating IP 192.0.2.1
    - Deleted floating IP 192.0.2.1
    - Floating IP would be created
    - Floating IP 192.0.2.1 does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class FloatingIP(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.region = module.params.get("region")
        self.droplet_id = module.params.get("droplet_id")
        self.ip = module.params.get("ip")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_floating_ip(self):
        if not self.ip:
            return None
        try:
            floating_ips = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.floating_ips,
                meth="list",
                key="floating_ips",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            for floating_ip in floating_ips:
                if self.ip == floating_ip.get("ip"):
                    return floating_ip
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
                floating_ip={},
            )

    def create_floating_ip(self):
        try:
            body = {}
            if self.droplet_id:
                body["droplet_id"] = self.droplet_id
            elif self.region:
                body["region"] = self.region
            else:
                self.module.fail_json(
                    changed=False,
                    msg="Either region or droplet_id is required",
                    floating_ip={},
                )

            floating_ip = self.client.floating_ips.create(body=body)["floating_ip"]

            self.module.exit_json(
                changed=True,
                msg=f"Created floating IP {floating_ip['ip']}",
                floating_ip=floating_ip,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, floating_ip={}
            )

    def delete_floating_ip(self, floating_ip):
        try:
            self.client.floating_ips.delete(floating_ip=floating_ip["ip"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted floating IP {floating_ip['ip']}",
                floating_ip=floating_ip,
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
                floating_ip={},
            )

    def present(self):
        if self.ip:
            floating_ip = self.get_floating_ip()
            if floating_ip:
                self.module.exit_json(
                    changed=False,
                    msg=f"Floating IP {self.ip} exists",
                    floating_ip=floating_ip,
                )
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg="Floating IP would be created",
                floating_ip={},
            )
        else:
            self.create_floating_ip()

    def absent(self):
        if not self.ip:
            self.module.fail_json(
                changed=False,
                msg="ip is required when deleting a floating IP",
                floating_ip={},
            )
        floating_ip = self.get_floating_ip()
        if floating_ip is None:
            self.module.exit_json(
                changed=False,
                msg=f"Floating IP {self.ip} does not exist",
                floating_ip={},
            )
        else:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Floating IP {self.ip} would be deleted",
                    floating_ip=floating_ip,
                )
            else:
                self.delete_floating_ip(floating_ip=floating_ip)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        region=dict(type="str", required=False),
        droplet_id=dict(type="int", required=False),
        ip=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    FloatingIP(module)


if __name__ == "__main__":
    main()
