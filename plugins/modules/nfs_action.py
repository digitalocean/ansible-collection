#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: nfs_action

short_description: Perform actions on NFS file shares

version_added: 1.9.0

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
      - attach
      - detach
  size_gib:
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
  vpc_id:
    description:
      - The VPC ID to attach/detach.
      - Required when type is C(attach) or C(detach).
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
    size_gib: 200

- name: Create NFS snapshot
  digitalocean.cloud.nfs_action:
    token: "{{ token }}"
    nfs_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    type: snapshot
    snapshot_name: my-nfs-snapshot

- name: Attach NFS share to VPC
  digitalocean.cloud.nfs_action:
    token: "{{ token }}"
    nfs_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    type: attach
    vpc_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e5

- name: Detach NFS share from VPC
  digitalocean.cloud.nfs_action:
    token: "{{ token }}"
    nfs_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    type: detach
    vpc_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e5
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
        self.size_gib = module.params.get("size_gib")
        self.snapshot_name = module.params.get("snapshot_name")
        self.vpc_id = module.params.get("vpc_id")

        if self.state == "present":
            self.present()

    def perform_action(self):
        try:
            body = {
                "type": self.action_type,
            }

            if self.action_type == "resize":
                if not self.size_gib:
                    self.module.fail_json(
                        changed=False,
                        msg="size_gib is required for resize action",
                        action={},
                    )
                body["size_gib"] = self.size_gib
            elif self.action_type == "snapshot":
                if not self.snapshot_name:
                    self.module.fail_json(
                        changed=False,
                        msg="snapshot_name is required for snapshot action",
                        action={},
                    )
                body["name"] = self.snapshot_name
            elif self.action_type in ("attach", "detach"):
                if not self.vpc_id:
                    self.module.fail_json(
                        changed=False,
                        msg=f"vpc_id is required for {self.action_type} action",
                        action={},
                    )
                body["vpc_id"] = self.vpc_id

            # API method is create_action, not post_action
            response = self.client.nfs.create_action(nfs_id=self.nfs_id, body=body)

            # Check if the response contains an error (API returns 200 with error payload)
            error_id = response.get("id") or response.get("code")
            error_msg = response.get("message")
            if error_id and error_msg and not response.get("action"):
                self.module.fail_json(
                    changed=False,
                    msg=error_msg,
                    error={
                        "Message": error_msg,
                        "id": error_id,
                        "request_id": response.get("request_id"),
                    },
                    action={},
                )

            action = response.get("action", response)
            if not action.get("id") and not action.get("status"):
                self.module.fail_json(
                    changed=False,
                    msg="API response missing expected action fields",
                    error={"Message": "Unexpected API response structure"},
                    action=action,
                )

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
                # NFS actions don't have get_action_by_id, just wait
                # Actions complete quickly for NFS

            self.module.exit_json(
                changed=True,
                msg=f"Completed {self.action_type} action on NFS share {self.nfs_id}",
                action=action,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message if err.error else str(err),
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                action={},
            )

    def present(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"NFS {self.action_type} action would be performed on {self.nfs_id}",
                action={},
            )
        else:
            self.perform_action()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        nfs_id=dict(type="str", required=True),
        type=dict(
            type="str",
            required=True,
            choices=["resize", "snapshot", "attach", "detach"],
        ),
        size_gib=dict(type="int", required=False),
        snapshot_name=dict(type="str", required=False),
        vpc_id=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("type", "resize", ["size_gib"]),
            ("type", "snapshot", ["snapshot_name"]),
            ("type", "attach", ["vpc_id"]),
            ("type", "detach", ["vpc_id"]),
        ],
    )
    NFSAction(module)


if __name__ == "__main__":
    main()
