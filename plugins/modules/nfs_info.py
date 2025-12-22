#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nfs_info

short_description: List all NFS file shares on your account

version_added: 0.6.0

description:
  - List all NFS file shares on your account.
  - |
    NFS (Network File System) provides shared file storage that can be
    mounted by multiple Droplets simultaneously.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/NFS).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get NFS shares
  digitalocean.cloud.nfs_info:
    token: "{{ token }}"
"""


RETURN = r"""
nfs_shares:
  description: NFS file shares.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      name: my-nfs-share
      region: nyc1
      size_gigabytes: 100
      droplet_ids:
        - 12345678
        - 87654321
      created_at: '2020-03-13T19:20:47.442049222Z'
      status: active
      mount_path: /mnt/nfs-share
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: NFS shares result information.
  returned: always
  type: str
  sample:
    - Current NFS shares
    - No NFS shares
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class NFSInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        nfs_shares = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.nfs,
            meth="list",
            key="nfs_shares",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if nfs_shares:
            self.module.exit_json(
                changed=False,
                msg="Current NFS shares",
                nfs_shares=nfs_shares,
            )
        self.module.exit_json(changed=False, msg="No NFS shares", nfs_shares=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    NFSInformation(module)


if __name__ == "__main__":
    main()
