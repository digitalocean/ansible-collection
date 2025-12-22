#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nfs_action

short_description: Perform actions on NFS file shares

version_added: 0.6.0

description:
  - Perform actions on NFS file shares such as resize and snapshot.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/NFS-Actions).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  nfs_id:
    description:
      - The unique identifier of the NFS share.
    type: str
    required: true
  type:
    description:
      - The type of action to perform.
    type: str
    required: true
    choices:
      - resize
      - snapshot
  size_gigabytes:
    description:
      - The new size of the NFS share in GiB.
      - Required when type is C(resize).
    type: int
    required: false
  snapshot_name:
    description:
      - The name for the snapshot.
      - Required when type is C(snapshot).
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Resize NFS share
  digitalocean.cloud.nfs_action:
    token: "{{ token }}"
    nfs_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    type: resize
    size_gigabytes: 200

- name: Create NFS snapshot
  digitalocean.cloud.nfs_action:
    token: "{{ token }}"
    nfs_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    type: snapshot
    snapshot_name: my-nfs-snapshot
"""


RETURN = r"""
action:
  description: NFS action information.
  returned: always
  type: dict
  sample:
    id: 12345678
    status: in-progress
    type: resize
    started_at: '2020-03-13T19:20:47.442049222Z'
    completed_at: null
    resource_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    resource_type: nfs
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: NFS action result information.
  returned: always
  type: str
  sample:
    - Initiated resize action on NFS share
    - Initiated snapshot action on NFS share
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanConstants,
)


class NFSAction(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.nfs_id = module.params.get("nfs_id")
        self.action_type = module.params.get("type")
        self.size_gigabytes = module.params.get("size_gigabytes")
        self.snapshot_name = module.params.get("snapshot_name")

        if self.state == "present":
            self.present()

    def perform_action(self):
        try:
            body = {
                "type": self.action_type,
            }

            if self.action_type == "resize":
                if not self.size_gigabytes:
                    self.module.fail_json(
                        changed=False,
                        msg="size_gigabytes is required for resize action",
                        action=[],
                    )
                body["size_gigabytes"] = self.size_gigabytes
            elif self.action_type == "snapshot":
                if not self.snapshot_name:
                    self.module.fail_json(
                        changed=False,
                        msg="snapshot_name is required for snapshot action",
                        action=[],
                    )
                body["name"] = self.snapshot_name

            action = self.client.nfs.post_action(nfs_id=self.nfs_id, body=body)[
                "action"
            ]

            # Wait for the action to complete
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                status = action.get("status", "").lower()
                if status == "completed":
                    break
                if status == "errored":
                    self.module.fail_json(
                        changed=True,
                        msg=f"NFS {self.action_type} action failed",
                        action=action,
                    )
                time.sleep(DigitalOceanConstants.SLEEP)
                action = self.get_action_by_id(action["id"])

            self.module.exit_json(
                changed=True,
                msg=f"Completed {self.action_type} action on NFS share {self.nfs_id}",
                action=action,
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
                action=[],
            )

    def present(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"NFS {self.action_type} action would be performed on {self.nfs_id}",
                action=[],
            )
        else:
            self.perform_action()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        nfs_id=dict(type="str", required=True),
        type=dict(type="str", required=True, choices=["resize", "snapshot"]),
        size_gigabytes=dict(type="int", required=False),
        snapshot_name=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("type", "resize", ["size_gigabytes"]),
            ("type", "snapshot", ["snapshot_name"]),
        ],
    )
    NFSAction(module)


if __name__ == "__main__":
    main()
