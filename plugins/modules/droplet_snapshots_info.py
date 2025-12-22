#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplet_snapshots_info

short_description: List snapshots for a Droplet

version_added: 0.6.0

description:
  - List all snapshots for a specific Droplet.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Droplets).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  droplet_id:
    description:
      - The ID of the Droplet to list snapshots for.
    type: int
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get Droplet snapshots
  digitalocean.cloud.droplet_snapshots_info:
    token: "{{ token }}"
    droplet_id: 12345678
"""


RETURN = r"""
snapshots:
  description: List of snapshots for the Droplet.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 12345678
      name: my-snapshot
      type: snapshot
      distribution: Ubuntu
      slug: null
      public: false
      regions:
        - nyc1
      created_at: '2023-01-01T00:00:00Z'
      min_disk_size: 25
      size_gigabytes: 2.5
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Droplet snapshots result information.
  returned: always
  type: str
  sample:
    - Snapshots for Droplet 12345678
    - No snapshots for Droplet 12345678
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class DropletSnapshotsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.droplet_id = module.params.get("droplet_id")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            snapshots = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.droplets,
                meth="list_snapshots",
                key="snapshots",
                exc=DigitalOceanCommonModule.HttpResponseError,
                droplet_id=self.droplet_id,
            )
            if snapshots:
                self.module.exit_json(
                    changed=False,
                    msg=f"Snapshots for Droplet {self.droplet_id}",
                    snapshots=snapshots,
                )
            self.module.exit_json(
                changed=False,
                msg=f"No snapshots for Droplet {self.droplet_id}",
                snapshots=[],
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
                snapshots=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        droplet_id=dict(type="int", required=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    DropletSnapshotsInformation(module)


if __name__ == "__main__":
    main()
