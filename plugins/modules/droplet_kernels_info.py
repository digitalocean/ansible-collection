#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplet_kernels_info

short_description: List available kernels for a Droplet

version_added: 1.9.0

description:
  - List all available kernels for a specific Droplet.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Droplets).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  droplet_id:
    description:
      - The ID of the Droplet to list available kernels for.
    type: int
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get available Droplet kernels
  digitalocean.cloud.droplet_kernels_info:
    token: "{{ token }}"
    droplet_id: 12345678
"""


RETURN = r"""
kernels:
  description: List of available kernels for the Droplet.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 123
      name: DigitalOcean GrubLoader v0.2 (20190819-0)
      version: "5.4.0-81"
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Droplet kernels result information.
  returned: always
  type: str
  sample:
    - Available kernels for Droplet 12345678
    - No available kernels for Droplet 12345678
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class DropletKernelsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.droplet_id = module.params.get("droplet_id")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            kernels = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.droplets,
                meth="list_kernels",
                key="kernels",
                exc=DigitalOceanCommonModule.HttpResponseError,
                droplet_id=self.droplet_id,
            )
            if kernels:
                self.module.exit_json(
                    changed=False,
                    msg=f"Available kernels for Droplet {self.droplet_id}",
                    kernels=kernels,
                )
            self.module.exit_json(
                changed=False,
                msg=f"No available kernels for Droplet {self.droplet_id}",
                kernels=[],
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
                kernels=[],
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
    DropletKernelsInformation(module)


if __name__ == "__main__":
    main()
