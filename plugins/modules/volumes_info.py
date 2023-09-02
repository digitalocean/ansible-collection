#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: volumes_info

short_description: List all of the block storage volumes available on your account

version_added: 0.2.0

description:
  - List all of the block storage volumes available on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/volumes_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get volumes
  digitalocean.cloud.volumes_info:
    token: "{{ token }}"
"""


RETURN = r"""
volumes:
  description: Volumes.
  returned: always
  type: list
  elements: dict
  sample:
    - created_at: '2022-11-28T02:07:45Z'
      description: Block store for examples
      droplet_ids: []
      filesystem_label: example
      filesystem_type: ext4
      id: 72b1d6de-6ec1-11ed-8a0d-0a58ac1466a8
      name: example
      region:
        available: true
        features:
          - backups
          - ipv6
          - metadata
          - install_agent
          - storage
          - image_transfer
        name: New York 3
        sizes:
          - s-1vcpu-1gb
          - s-1vcpu-1gb-amd
          - s-1vcpu-1gb-intel
          - ...
        slug: nyc3
      size_gigabytes: 1
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
  description: Volumes result information.
  returned: always
  type: str
  sample:
    - Current volumes
    - No volumes
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class VolumesInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        volumes = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.volumes,
            meth="list",
            key="volumes",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if volumes:
            self.module.exit_json(
                changed=False,
                msg="Current volumes",
                volumes=volumes,
            )
        self.module.exit_json(changed=False, msg="No volumes", volumes=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    VolumesInformation(module)


if __name__ == "__main__":
    main()
