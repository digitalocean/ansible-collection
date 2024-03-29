#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: snapshots_info

short_description: Retrieve a list of all of the snapshots in your account

version_added: 0.2.0

description:
  - Retrieve a list of all of the snapshots in your account.
  - View the API documentation at (https://docs.digitalocean.com/reference/api/api-reference/#operation/snapshots_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  resource_type:
    description: Used to filter snapshots by a resource type.
    type: str
    required: false
    choices: [ droplet, volume ]

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get snapshots
  digitalocean.cloud.snapshots_info:
    token: "{{ token }}"

- name: Get Droplet snapshots
  digitalocean.cloud.snapshots_info:
    token: "{{ token }}"
    type: droplet

- name: Get volume snapshots
  digitalocean.cloud.snapshots_info:
    token: "{{ token }}"
    type: volume
"""


RETURN = r"""
snapshots:
  description: Snapshots.
  returned: always
  type: list
  elements: dict
  sample:
    - id: '6372321'
      name: web-01-1595954862243
      created_at: '2020-07-28T16:47:44Z'
      regions: []
      resource_id: '200776916'
      resource_type: droplet
      min_disk_size: 25
      size_gigabytes: 2.34
      tags: []
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Snapshots result information.
  returned: always
  type: str
  sample:
    - Current snapshots
    - No snapshots
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class SnapshotsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.resource_type = module.params.get("resource_type")
        self.params = {}
        if self.resource_type:
            self.params.update(dict(resource_type=self.resource_type))
        if self.state == "present":
            self.present()

    def present(self):
        snapshots = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.snapshots,
            meth="list",
            key="snapshots",
            params=self.params,
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if snapshots:
            self.module.exit_json(
                changed=False,
                msg="Current snapshots",
                snapshots=snapshots,
            )
        self.module.exit_json(changed=False, msg="No snapshots", snapshots=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        resource_type=dict(type="str", choices=["droplet", "volume"], required=False)
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    SnapshotsInformation(module)


if __name__ == "__main__":
    main()
