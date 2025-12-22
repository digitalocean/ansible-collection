#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: function_namespaces_info

short_description: List all Functions namespaces on your account

version_added: 0.6.0

description:
  - List all Functions namespaces on your account.
  - |
    DigitalOcean Functions is a serverless computing solution that runs
    on-demand, allowing you to focus on code without managing infrastructure.
    Namespaces are containers for functions.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Functions).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get Functions namespaces
  digitalocean.cloud.function_namespaces_info:
    token: "{{ token }}"
"""


RETURN = r"""
namespaces:
  description: Functions namespaces.
  returned: always
  type: list
  elements: dict
  sample:
    - namespace: my-namespace
      region: nyc1
      uuid: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      created_at: '2020-03-13T19:20:47.442049222Z'
      updated_at: '2020-03-13T19:20:47.442049222Z'
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Functions namespaces result information.
  returned: always
  type: str
  sample:
    - Current namespaces
    - No namespaces
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class FunctionNamespacesInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        namespaces = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.functions,
            meth="list_namespaces",
            key="namespaces",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if namespaces:
            self.module.exit_json(
                changed=False,
                msg="Current namespaces",
                namespaces=namespaces,
            )
        self.module.exit_json(changed=False, msg="No namespaces", namespaces=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    FunctionNamespacesInformation(module)


if __name__ == "__main__":
    main()
