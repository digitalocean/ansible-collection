#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nfs_info

short_description: List all NFS file shares on your account

version_added: 1.9.0

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

options:
  region:
    description:
      - The slug identifier for the region to list NFS shares from.
    type: str
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get NFS shares in nyc3
  digitalocean.cloud.nfs_info:
    token: "{{ token }}"
    region: nyc3
"""


RETURN = r"""
shares:
  description: NFS file shares.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      name: my-nfs-share
      region: nyc3
      size_gib: 100
      vpc_ids:
        - "5a4981aa-9653-4bd1-bef5-d6bff52042e4"
      created_at: '2020-03-13T19:20:47.442049222Z'
      status: ACTIVE
      mount_path: /mnt/nfs-share
      host: 10.132.0.2
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
)


class NFSInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.region = module.params.get("region")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            # NFS API returns "shares" key, not "nfs_shares"
            response = self.client.nfs.list(region=self.region)
            shares = response.get("shares", [])
            if shares:
                self.module.exit_json(
                    changed=False,
                    msg="Current NFS shares",
                    shares=shares,
                )
            self.module.exit_json(changed=False, msg="No NFS shares", shares=[])
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message if err.error else str(err),
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, shares=[]
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        region=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    NFSInformation(module)


if __name__ == "__main__":
    main()
