#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: byoip_prefix

short_description: Manage Bring Your Own IP (BYOIP) prefixes

version_added: 0.6.0

description:
  - Create or delete Bring Your Own IP (BYOIP) prefixes.
  - |
    BYOIP allows you to use your own IP address ranges with DigitalOcean
    infrastructure. You can announce your own IP prefixes and assign them
    to your Droplets.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/BYOIP-Prefixes).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  prefix:
    description:
      - The IP prefix in CIDR notation (e.g., 192.0.2.0/24).
    type: str
    required: true
  description:
    description:
      - A description for the BYOIP prefix.
    type: str
    required: false
  id:
    description:
      - The unique identifier of the BYOIP prefix.
      - Used for lookup when deleting or updating.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create BYOIP prefix
  digitalocean.cloud.byoip_prefix:
    token: "{{ token }}"
    state: present
    prefix: 192.0.2.0/24
    description: My custom IP range

- name: Delete BYOIP prefix
  digitalocean.cloud.byoip_prefix:
    token: "{{ token }}"
    state: absent
    prefix: 192.0.2.0/24
"""


RETURN = r"""
byoip_prefix:
  description: BYOIP prefix information.
  returned: always
  type: dict
  sample:
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
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
  description: BYOIP prefix result information.
  returned: always
  type: str
  sample:
    - Created BYOIP prefix 192.0.2.0/24
    - Deleted BYOIP prefix 192.0.2.0/24
    - BYOIP prefix 192.0.2.0/24 would be created
    - BYOIP prefix 192.0.2.0/24 exists
    - BYOIP prefix 192.0.2.0/24 does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class BYOIPPrefix(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.prefix = module.params.get("prefix")
        self.description = module.params.get("description")
        self.id = module.params.get("id")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_byoip_prefixes(self):
        try:
            byoip_prefixes = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.byoip_prefixes,
                meth="list",
                key="byoip_prefixes",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            found_prefixes = []
            for byoip_prefix in byoip_prefixes:
                if self.prefix == byoip_prefix.get("prefix"):
                    found_prefixes.append(byoip_prefix)
                elif self.id and self.id == byoip_prefix.get("id"):
                    found_prefixes.append(byoip_prefix)
            return found_prefixes
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
                byoip_prefix={},
            )

    def create_byoip_prefix(self):
        try:
            body = {
                "prefix": self.prefix,
            }
            if self.description:
                body["description"] = self.description

            byoip_prefix = self.client.byoip_prefixes.create(body=body)["byoip_prefix"]

            self.module.exit_json(
                changed=True,
                msg=f"Created BYOIP prefix {self.prefix}",
                byoip_prefix=byoip_prefix,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, byoip_prefix={}
            )

    def delete_byoip_prefix(self, byoip_prefix):
        try:
            self.client.byoip_prefixes.delete(byoip_prefix_id=byoip_prefix["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted BYOIP prefix {self.prefix}",
                byoip_prefix=byoip_prefix,
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
                byoip_prefix={},
            )

    def present(self):
        byoip_prefixes = self.get_byoip_prefixes()
        if len(byoip_prefixes) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"BYOIP prefix {self.prefix} would be created",
                    byoip_prefix={},
                )
            else:
                self.create_byoip_prefix()
        elif len(byoip_prefixes) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"BYOIP prefix {self.prefix} exists",
                byoip_prefix=byoip_prefixes[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(byoip_prefixes)} BYOIP prefixes matching {self.prefix}",
                byoip_prefix={},
            )

    def absent(self):
        byoip_prefixes = self.get_byoip_prefixes()
        if len(byoip_prefixes) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"BYOIP prefix {self.prefix} does not exist",
                byoip_prefix={},
            )
        elif len(byoip_prefixes) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"BYOIP prefix {self.prefix} would be deleted",
                    byoip_prefix=byoip_prefixes[0],
                )
            else:
                self.delete_byoip_prefix(byoip_prefix=byoip_prefixes[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(byoip_prefixes)} BYOIP prefixes matching {self.prefix}",
                byoip_prefix={},
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        prefix=dict(type="str", required=True),
        description=dict(type="str", required=False),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    BYOIPPrefix(module)


if __name__ == "__main__":
    main()
