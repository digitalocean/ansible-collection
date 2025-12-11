#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: cdn_endpoints_info

short_description: List all of the CDN endpoints available on your account

version_added: 0.2.0

description:
  - List all of the CDN endpoints available on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/cdn_list_endpoints).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get CDN endpoints
  digitalocean.cloud.cdn_endpoints_info:
    token: "{{ token }}"
"""


RETURN = r"""
endpoints:
  description: CDN endpoints.
  returned: always
  type: list
  sample:
    - id: 19f06b6a-3ace-4315-b086-499a0e521b76
      origin: static-images.nyc3.digitaloceanspaces.com
      endpoint: static-images.nyc3.cdn.digitaloceanspaces.com
      created_at: '2018-07-19T15:04:16Z'
      certificate_id: 892071a0-bb95-49bc-8021-3afd67a210bf
      custom_domain: static.example.com
      ttl: 3600
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: CDN endpoints result information.
  returned: always
  type: str
  sample:
    - Current CDN endpoints
    - No CDN endpoints
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanFunctions,
    DigitalOceanOptions,
)


class CDNEndpointsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        cdn_endpoints = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.cdn,
            meth="list_endpoints",
            key="endpoints",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if cdn_endpoints:
            self.module.exit_json(
                changed=False,
                msg="Current CDN endpoints",
                endpoints=cdn_endpoints,
            )
        self.module.exit_json(changed=False, msg="No CDN endpoints", endpoints=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    CDNEndpointsInformation(module)


if __name__ == "__main__":
    main()
