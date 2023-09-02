#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: firewalls_info

short_description: List all firewalls on your account

version_added: 0.2.0

description:
  - List all firewall on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/firewalls_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get firewalls
  digitalocean.cloud.firewalls_info:
    token: "{{ token }}"
"""


RETURN = r"""
firewalls:
  description: Firewalls.
  returned: always
  type: list
  elements: dict
  sample:
    - id: fb6045f1-cf1d-4ca3-bfac-18832663025b
      name: firewall
      status: succeeded
      inbound_rules:
        - protocol: tcp
          ports: '80'
          sources:
            load_balancer_uids:
              - 4de7ac8b-495b-4884-9a69-1050c6793cd6
        - protocol: tcp
          ports: '22'
          sources:
            tags:
              - gateway
            addresses:
              - 18.0.0.0/8
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Firewalls result information.
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
    DigitalOceanFunctions,
)


class FirewallsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        firewalls = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.firewalls,
            meth="list",
            key="firewalls",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if firewalls:
            self.module.exit_json(
                changed=False,
                msg="Current firewalls",
                firewalls=firewalls,
            )
        self.module.exit_json(changed=False, msg="No firewalls", firewalls=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    FirewallsInformation(module)


if __name__ == "__main__":
    main()
