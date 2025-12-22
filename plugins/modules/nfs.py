#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nfs

short_description: Create or delete NFS file shares

version_added: 0.6.0

description:
  - Create or delete NFS file shares.
  - |
    NFS (Network File System) provides shared file storage that can be
    mounted by multiple Droplets simultaneously.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/NFS).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The name of the NFS share.
    type: str
    required: true
  region:
    description:
      - The slug identifier for the region where the NFS share will be created.
    type: str
    required: false
  size_gigabytes:
    description:
      - The size of the NFS share in GiB.
    type: int
    required: false
  droplet_ids:
    description:
      - An array of Droplet IDs that should have access to the NFS share.
    type: list
    elements: int
    required: false
  tags:
    description:
      - A list of tags to apply to the NFS share.
    type: list
    elements: str
    required: false
  id:
    description:
      - The unique identifier of the NFS share.
      - Used for lookup when deleting or updating.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create NFS share
  digitalocean.cloud.nfs:
    token: "{{ token }}"
    state: present
    name: my-nfs-share
    region: nyc1
    size_gigabytes: 100
    droplet_ids:
      - 12345678
      - 87654321

- name: Delete NFS share by name
  digitalocean.cloud.nfs:
    token: "{{ token }}"
    state: absent
    name: my-nfs-share

- name: Delete NFS share by ID
  digitalocean.cloud.nfs:
    token: "{{ token }}"
    state: absent
    name: my-nfs-share
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
"""


RETURN = r"""
nfs:
  description: NFS share information.
  returned: always
  type: dict
  sample:
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
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
  description: NFS share result information.
  returned: always
  type: str
  sample:
    - Created NFS share my-nfs-share (5a4981aa-9653-4bd1-bef5-d6bff52042e4)
    - Deleted NFS share my-nfs-share (5a4981aa-9653-4bd1-bef5-d6bff52042e4)
    - NFS share my-nfs-share would be created
    - NFS share my-nfs-share (5a4981aa-9653-4bd1-bef5-d6bff52042e4) exists
    - NFS share my-nfs-share does not exist
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
    DigitalOceanConstants,
)


class NFS(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.region = module.params.get("region")
        self.size_gigabytes = module.params.get("size_gigabytes")
        self.droplet_ids = module.params.get("droplet_ids")
        self.tags = module.params.get("tags")
        self.id = module.params.get("id")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_nfs_shares(self):
        try:
            nfs_shares = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.nfs,
                meth="list",
                key="nfs_shares",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            found_shares = []
            for share in nfs_shares:
                if self.name == share.get("name"):
                    found_shares.append(share)
                elif self.id and self.id == share.get("id"):
                    found_shares.append(share)
            return found_shares
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
                nfs=[],
            )

    def create_nfs_share(self):
        try:
            body = {
                "name": self.name,
            }
            if self.region:
                body["region"] = self.region
            if self.size_gigabytes:
                body["size_gigabytes"] = self.size_gigabytes
            if self.droplet_ids:
                body["droplet_ids"] = self.droplet_ids
            if self.tags:
                body["tags"] = self.tags

            nfs_share = self.client.nfs.create(body=body)["nfs_share"]

            # Wait for the NFS share to become active
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                status = nfs_share.get("status", "").lower()
                if status == "active":
                    break
                time.sleep(DigitalOceanConstants.SLEEP)
                try:
                    nfs_share = self.client.nfs.get(nfs_id=nfs_share["id"])["nfs_share"]
                except DigitalOceanCommonModule.HttpResponseError:
                    pass

            self.module.exit_json(
                changed=True,
                msg=f"Created NFS share {self.name} ({nfs_share['id']})",
                nfs=nfs_share,
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
                nfs=[],
            )

    def delete_nfs_share(self, nfs_share):
        try:
            self.client.nfs.delete(nfs_id=nfs_share["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted NFS share {self.name} ({nfs_share['id']})",
                nfs=nfs_share,
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
                nfs=[],
            )

    def present(self):
        nfs_shares = self.get_nfs_shares()
        if len(nfs_shares) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"NFS share {self.name} would be created",
                    nfs=[],
                )
            else:
                self.create_nfs_share()
        elif len(nfs_shares) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"NFS share {self.name} ({nfs_shares[0]['id']}) exists",
                nfs=nfs_shares[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(nfs_shares)} NFS shares named {self.name}",
                nfs=[],
            )

    def absent(self):
        nfs_shares = self.get_nfs_shares()
        if len(nfs_shares) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"NFS share {self.name} does not exist",
                nfs=[],
            )
        elif len(nfs_shares) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"NFS share {self.name} ({nfs_shares[0]['id']}) would be deleted",
                    nfs=nfs_shares[0],
                )
            else:
                self.delete_nfs_share(nfs_share=nfs_shares[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(nfs_shares)} NFS shares named {self.name}",
                nfs=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        region=dict(type="str", required=False),
        size_gigabytes=dict(type="int", required=False),
        droplet_ids=dict(type="list", elements="int", required=False),
        tags=dict(type="list", elements="str", required=False),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    NFS(module)


if __name__ == "__main__":
    main()
