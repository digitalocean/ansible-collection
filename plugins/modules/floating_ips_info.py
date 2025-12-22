#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: floating_ips_info

short_description: List all floating IPs on your account (legacy)

version_added: 0.6.0

description:
  - List all floating IPs on your account.
  - |
    NOTE: Floating IPs have been renamed to Reserved IPs. This module is
    provided for backwards compatibility. New implementations should use
    the reserved_ips_info module instead.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Floating-IPs).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get floating IPs
  digitalocean.cloud.floating_ips_info:
    token: "{{ token }}"
"""


RETURN = r"""
floating_ips:
  description: Floating IPs.
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
        available: true
        sizes:
          - s-1vcpu-1gb
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
  description: Floating IPs result information.
  returned: always
  type: str
  sample:
    - Current floating IPs
    - No floating IPs
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class FloatingIPsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        try:
            floating_ips = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.floating_ips,
                meth="list",
                key="floating_ips",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            if floating_ips:
                self.module.exit_json(
                    changed=False, msg="Current floating IPs", floating_ips=floating_ips
                )
            self.module.exit_json(changed=False, msg="No floating IPs", floating_ips=[])
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, floating_ips=[]
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    FloatingIPsInformation(module)


if __name__ == "__main__":
    main()
