#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplet_neighbors_info

short_description: List Droplet neighbors

version_added: 0.6.0

description:
  - List all Droplets that are co-located on the same physical hardware.
  - |
    Droplet neighbors are Droplets that share the same physical server.
    This information can be useful for planning high-availability deployments.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Droplets).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  droplet_id:
    description:
      - The ID of a specific Droplet to get neighbors for.
      - If not specified, returns all neighbor groupings for all Droplets.
    type: int
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get all Droplet neighbor groupings
  digitalocean.cloud.droplet_neighbors_info:
    token: "{{ token }}"

- name: Get neighbors for a specific Droplet
  digitalocean.cloud.droplet_neighbors_info:
    token: "{{ token }}"
    droplet_id: 12345678
"""


RETURN = r"""
neighbors:
  description: Lists of Droplet IDs that are on the same physical hardware.
  returned: always
  type: list
  elements: list
  sample:
    - - 12345678
      - 87654321
    - - 11111111
      - 22222222
      - 33333333
droplets:
  description: Full Droplet information when querying a specific Droplet's neighbors.
  returned: when droplet_id is specified
  type: list
  elements: dict
  sample:
    - id: 87654321
      name: neighbor-droplet
      status: active
      region:
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
  description: Droplet neighbors result information.
  returned: always
  type: str
  sample:
    - Current Droplet neighbors
    - No Droplet neighbors
    - Neighbors for Droplet 12345678
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class DropletNeighborsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.droplet_id = module.params.get("droplet_id")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            if self.droplet_id:
                # Get neighbors for a specific Droplet
                response = self.client.droplets.list_neighbors(
                    droplet_id=self.droplet_id
                )
                droplets = response.get("droplets", [])
                if droplets:
                    self.module.exit_json(
                        changed=False,
                        msg=f"Neighbors for Droplet {self.droplet_id}",
                        droplets=droplets,
                        neighbors=[],
                    )
                self.module.exit_json(
                    changed=False,
                    msg=f"No neighbors for Droplet {self.droplet_id}",
                    droplets=[],
                    neighbors=[],
                )
            else:
                # Get all Droplet neighbor groupings
                neighbors = DigitalOceanFunctions.get_paginated(
                    module=self.module,
                    obj=self.client.droplets,
                    meth="list_all_neighbors",
                    key="neighbors",
                    exc=DigitalOceanCommonModule.HttpResponseError,
                )
                if neighbors:
                    self.module.exit_json(
                        changed=False,
                        msg="Current Droplet neighbors",
                        neighbors=neighbors,
                        droplets=[],
                    )
                self.module.exit_json(
                    changed=False,
                    msg="No Droplet neighbors",
                    neighbors=[],
                    droplets=[],
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
                neighbors=[],
                droplets=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        droplet_id=dict(type="int", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    DropletNeighborsInformation(module)


if __name__ == "__main__":
    main()
