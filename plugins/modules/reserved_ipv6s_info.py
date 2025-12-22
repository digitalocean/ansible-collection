#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: reserved_ipv6s_info

short_description: List all reserved IPv6 addresses on your account

version_added: 0.6.0

description:
  - List all reserved IPv6 addresses on your account.
  - |
    Reserved IPv6 addresses are static addresses that can be assigned to
    Droplets and retained across Droplet deletion and recreation.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Reserved-IPv6).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get reserved IPv6 addresses
  digitalocean.cloud.reserved_ipv6s_info:
    token: "{{ token }}"
"""


RETURN = r"""
reserved_ipv6s:
  description: Reserved IPv6 addresses.
  returned: always
  type: list
  elements: dict
  sample:
    - ip: "2604:a880:800:10::1"
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
  description: Reserved IPv6 addresses result information.
  returned: always
  type: str
  sample:
    - Current reserved IPv6 addresses
    - No reserved IPv6 addresses
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class ReservedIPv6sInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        reserved_ipv6s = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.reserved_ipv6,
            meth="list",
            key="reserved_ipv6s",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if reserved_ipv6s:
            self.module.exit_json(
                changed=False,
                msg="Current reserved IPv6 addresses",
                reserved_ipv6s=reserved_ipv6s,
            )
        self.module.exit_json(
            changed=False, msg="No reserved IPv6 addresses", reserved_ipv6s=[]
        )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    ReservedIPv6sInformation(module)


if __name__ == "__main__":
    main()
