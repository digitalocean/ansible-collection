#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nfs

short_description: Create or delete NFS file shares

version_added: 1.9.0

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
    required: true
  size_gib:
    description:
      - The size of the NFS share in GiB (Gibibytes). Must be >= 50.
    type: int
    required: false
  vpc_ids:
    description:
      - List of VPC IDs that should be able to access the share.
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
    region: nyc3
    size_gib: 100
    vpc_ids:
      - "5a4981aa-9653-4bd1-bef5-d6bff52042e4"

- name: Delete NFS share by name
  digitalocean.cloud.nfs:
    token: "{{ token }}"
    state: absent
    name: my-nfs-share
    region: nyc3

- name: Delete NFS share by ID
  digitalocean.cloud.nfs:
    token: "{{ token }}"
    state: absent
    name: my-nfs-share
    region: nyc3
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
    DigitalOceanConstants,
)


class NFS(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.region = module.params.get("region")
        self.size_gib = module.params.get("size_gib")
        self.vpc_ids = module.params.get("vpc_ids")
        self.id = module.params.get("id")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_nfs_shares(self):
        try:
            # NFS API returns "shares" key, not "nfs_shares"
            response = self.client.nfs.list(region=self.region)
            shares = response.get("shares", [])
            found_shares = []
            for share in shares:
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
                nfs={},
            )

    def create_nfs_share(self):
        try:
            body = {
                "name": self.name,
                "region": self.region,
            }
            if self.size_gib:
                body["size_gib"] = self.size_gib
            if self.vpc_ids:
                body["vpc_ids"] = self.vpc_ids

            # API returns "share" key, not "nfs_share"
            response = self.client.nfs.create(body=body)

            # Check if the response contains an error (API returns 200 with error payload)
            # Some APIs use "id" + "message", others use "code" + "message"
            error_id = response.get("id") or response.get("code")
            error_msg = response.get("message")
            if error_id and error_msg and not response.get("share"):
                self.module.fail_json(
                    changed=False,
                    msg=error_msg,
                    error={
                        "Message": error_msg,
                        "id": error_id,
                        "request_id": response.get("request_id"),
                    },
                    nfs={},
                )

            nfs_share = response.get("share", response)
            nfs_id = nfs_share.get("id")

            if not nfs_id:
                self.module.fail_json(
                    changed=False,
                    msg="API response missing 'id' field",
                    error={"Message": "Unexpected API response structure"},
                    nfs=nfs_share,
                )

            # Wait for the NFS share to become active
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                status = nfs_share.get("status", "").upper()
                if status == "ACTIVE":
                    break
                time.sleep(DigitalOceanConstants.SLEEP)
                try:
                    # get() requires region parameter
                    response = self.client.nfs.get(nfs_id=nfs_id, region=self.region)
                    nfs_share = response.get("share", response)
                except DigitalOceanCommonModule.HttpResponseError:
                    pass

            self.module.exit_json(
                changed=True,
                msg=f"Created NFS share {self.name} ({nfs_id})",
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
                nfs={},
            )

    def delete_nfs_share(self, nfs_share):
        try:
            # delete() requires region parameter
            self.client.nfs.delete(nfs_id=nfs_share["id"], region=self.region)
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
                nfs={},
            )

    def present(self):
        nfs_shares = self.get_nfs_shares()
        if len(nfs_shares) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"NFS share {self.name} would be created",
                    nfs={},
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
                nfs={},
            )

    def absent(self):
        nfs_shares = self.get_nfs_shares()
        if len(nfs_shares) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"NFS share {self.name} does not exist",
                nfs={},
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
                nfs={},
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        region=dict(type="str", required=True),
        size_gib=dict(type="int", required=False),
        vpc_ids=dict(type="list", elements="str", required=False),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    NFS(module)


if __name__ == "__main__":
    main()
