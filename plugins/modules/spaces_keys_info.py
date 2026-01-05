#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: spaces_keys_info

short_description: List all Spaces access keys on your account

version_added: 1.9.0

description:
  - List all Spaces access keys on your account.
  - |
    Spaces access keys are used to authenticate with DigitalOcean Spaces,
    the S3-compatible object storage service.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Spaces-Keys).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get Spaces access keys
  digitalocean.cloud.spaces_keys_info:
    token: "{{ token }}"
"""


RETURN = r"""
spaces_keys:
  description: Spaces access keys.
  returned: always
  type: list
  elements: dict
  sample:
    - name: my-spaces-key
      access_key: AKIAIOSFODNN7EXAMPLE
      grants:
        - bucket: my-bucket
          permission: readwrite
      created_at: '2020-03-13T19:20:47.442049222Z'
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Spaces access keys result information.
  returned: always
  type: str
  sample:
    - Current Spaces access keys
    - No Spaces access keys
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class SpacesKeysInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        spaces_keys = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.spaces_keys,
            meth="list",
            key="keys",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if spaces_keys:
            self.module.exit_json(
                changed=False,
                msg="Current Spaces access keys",
                spaces_keys=spaces_keys,
            )
        self.module.exit_json(
            changed=False, msg="No Spaces access keys", spaces_keys=[]
        )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    SpacesKeysInformation(module)


if __name__ == "__main__":
    main()
