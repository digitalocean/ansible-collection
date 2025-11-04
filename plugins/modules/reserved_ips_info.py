#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: reserved_ips_info

short_description: List all reserved IPs on your account

version_added: 0.2.0

description:
  - List all reserved IPs on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/reservedIPs_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get reserved IPs
  digitalocean.cloud.reserved_ips_info:
    token: "{{ token }}"
"""


RETURN = r"""
reserved_ips:
  description: Reserved IPs.
  returned: always
  type: list
  elements: dict
  sample:
    - ip: 45.55.96.47
      droplet: null
      region:
        name: New York 3
        slug: nyc3
        features:
          - private_networking
          - backups
          - ipv6
          - metadata
          - install_agent
          - storage
          - image_transfer
        available: true
        sizes:
          - s-1vcpu-1gb
          - ...
      locked: false
      project_id: 746c6152-2fa2-11ed-92d3-27aaa54e4988
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Reserved IPs result information.
  returned: always
  type: str
  sample:
    - Current Droplets
    - No Droplets
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class ReservedIPsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        try:
            reserved_ips_response = self.client.reserved_ips.list()
            reserved_ips = reserved_ips_response.get("reserved_ips", [])
            if reserved_ips:
                self.module.exit_json(
                    changed=False, msg="Current reserved IPs", reserved_ips=reserved_ips
                )
            self.module.exit_json(changed=False, msg="No reserved IPs", reserved_ips=[])
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, reserved_ips=[]
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    ReservedIPsInformation(module)


if __name__ == "__main__":
    main()
