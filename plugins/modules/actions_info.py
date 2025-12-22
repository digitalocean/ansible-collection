#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: actions_info

short_description: List all actions that have been executed on your account

version_added: 0.6.0

description:
  - List all actions that have been executed on your account.
  - |
    Actions are records of events that have occurred on resources in your
    account. These can be things like rebooting a Droplet or transferring
    an image to a new region.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Actions).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  resource_type:
    description:
      - Used to filter actions by a specific resource type.
    type: str
    required: false
    choices:
      - droplet
      - image
      - volume
      - floating_ip
      - reserved_ip

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get all actions
  digitalocean.cloud.actions_info:
    token: "{{ token }}"

- name: Get Droplet actions
  digitalocean.cloud.actions_info:
    token: "{{ token }}"
    resource_type: droplet
"""


RETURN = r"""
actions:
  description: Actions.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 12345678
      status: completed
      type: create
      started_at: '2020-03-13T19:20:47.442049222Z'
      completed_at: '2020-03-13T19:21:47.442049222Z'
      resource_id: 12345678
      resource_type: droplet
      region:
        name: New York 1
        slug: nyc1
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Actions result information.
  returned: always
  type: str
  sample:
    - Current actions
    - No actions
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class ActionsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.resource_type = module.params.get("resource_type")
        self.params = {}
        if self.resource_type:
            self.params["resource_type"] = self.resource_type
        if self.state == "present":
            self.present()

    def present(self):
        actions = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.actions,
            meth="list",
            key="actions",
            exc=DigitalOceanCommonModule.HttpResponseError,
            params=self.params if self.params else None,
        )
        if actions:
            self.module.exit_json(
                changed=False,
                msg="Current actions",
                actions=actions,
            )
        self.module.exit_json(changed=False, msg="No actions", actions=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        resource_type=dict(
            type="str",
            required=False,
            choices=["droplet", "image", "volume", "floating_ip", "reserved_ip"],
        ),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    ActionsInformation(module)


if __name__ == "__main__":
    main()
