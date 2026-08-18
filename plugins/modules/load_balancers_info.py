#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: load_balancers_info

short_description: Retrieve a list of all of the load balancers in your account

version_added: 0.2.0

description:
  - Retrieve a list of all of the load balancers in your account.
  - View the API documentation at (https://docs.digitalocean.com/reference/api/api-reference/#operation/loadBalancers_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get load balancers
  digitalocean.cloud.load_balancers_info:
    token: "{{ token }}"
"""


RETURN = r"""
load_balancers:
  description: Load balancers.
  returned: always
  type: list
  elements: dict
  sample: []
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Domain result information.
  returned: always
  type: str
  sample:
    - Current domains
    - No domains
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanFunctions,
    DigitalOceanOptions,
)


class LoadBalancersInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        load_balancers = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.load_balancers,
            meth="list",
            key="load_balancers",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if load_balancers:
            self.module.exit_json(
                changed=False,
                msg="Current load balancers",
                load_balancers=load_balancers,
            )
        self.module.exit_json(
            changed=False, msg="No load balancers", load_balancers=load_balancers
        )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    LoadBalancersInformation(module)


if __name__ == "__main__":
    main()
