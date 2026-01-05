#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: byoip_prefixes_info

short_description: List all BYOIP prefixes on your account

version_added: 1.9.0

description:
  - List all Bring Your Own IP (BYOIP) prefixes on your account.
  - |
    BYOIP allows you to use your own IP address ranges with DigitalOcean
    infrastructure. You can announce your own IP prefixes and assign them
    to your Droplets.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/BYOIP-Prefixes).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get BYOIP prefixes
  digitalocean.cloud.byoip_prefixes_info:
    token: "{{ token }}"
"""


RETURN = r"""
byoip_prefixes:
  description: BYOIP prefixes.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      prefix: 192.0.2.0/24
      description: My custom IP range
      created_at: '2020-03-13T19:20:47.442049222Z'
      status: active
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: BYOIP prefixes result information.
  returned: always
  type: str
  sample:
    - Current BYOIP prefixes
    - No BYOIP prefixes
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class BYOIPPrefixesInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        byoip_prefixes = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.byoip_prefixes,
            meth="list",
            key="byoip_prefixes",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if byoip_prefixes:
            self.module.exit_json(
                changed=False,
                msg="Current BYOIP prefixes",
                byoip_prefixes=byoip_prefixes,
            )
        self.module.exit_json(changed=False, msg="No BYOIP prefixes", byoip_prefixes=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    BYOIPPrefixesInformation(module)


if __name__ == "__main__":
    main()
