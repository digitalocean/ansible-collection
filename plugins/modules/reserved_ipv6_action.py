#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: reserved_ipv6_action

short_description: Assign or unassign a reserved IPv6 address to a Droplet

version_added: 0.6.0

description:
  - Assign or unassign a reserved IPv6 address to a Droplet.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Reserved-IPv6-Actions).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  ip:
    description:
      - The reserved IPv6 address.
    type: str
    required: true
  type:
    description:
      - The type of action to perform.
    type: str
    required: true
    choices:
      - assign
      - unassign
  droplet_id:
    description:
      - The unique identifier of the Droplet to assign or unassign.
      - Required when type is C(assign).
    type: int
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Assign reserved IPv6 to Droplet
  digitalocean.cloud.reserved_ipv6_action:
    token: "{{ token }}"
    ip: "2604:a880:800:10::1"
    type: assign
    droplet_id: 12345678

- name: Unassign reserved IPv6 from Droplet
  digitalocean.cloud.reserved_ipv6_action:
    token: "{{ token }}"
    ip: "2604:a880:800:10::1"
    type: unassign
"""


RETURN = r"""
action:
  description: Reserved IPv6 action information.
  returned: always
  type: dict
  sample:
    id: 12345678
    status: completed
    type: assign
    started_at: '2020-03-13T19:20:47.442049222Z'
    completed_at: '2020-03-13T19:21:47.442049222Z'
    resource_id: 12345678
    resource_type: reserved_ipv6
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Reserved IPv6 action result information.
  returned: always
  type: str
  sample:
    - Assigned reserved IPv6 to Droplet
    - Unassigned reserved IPv6 from Droplet
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanConstants,
)


class ReservedIPv6Action(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.ip = module.params.get("ip")
        self.action_type = module.params.get("type")
        self.droplet_id = module.params.get("droplet_id")

        if self.state == "present":
            self.present()

    def perform_action(self):
        try:
            body = {
                "type": self.action_type,
            }

            if self.action_type == "assign":
                if not self.droplet_id:
                    self.module.fail_json(
                        changed=False,
                        msg="droplet_id is required for assign action",
                        action={},
                    )
                body["droplet_id"] = self.droplet_id

            action = self.client.reserved_ipv6_actions.post(
                reserved_ip=self.ip, body=body
            )["action"]

            # Wait for the action to complete
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                status = action.get("status", "").lower()
                if status == "completed":
                    break
                if status == "errored":
                    self.module.fail_json(
                        changed=True,
                        msg=f"Reserved IPv6 {self.action_type} action failed",
                        action=action,
                    )
                time.sleep(DigitalOceanConstants.SLEEP)
                action = self.get_action_by_id(action["id"])

            if self.action_type == "assign":
                msg = f"Assigned reserved IPv6 {self.ip} to Droplet {self.droplet_id}"
            else:
                msg = f"Unassigned reserved IPv6 {self.ip}"

            self.module.exit_json(
                changed=True,
                msg=msg,
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
                action={},
            )

    def present(self):
        if self.module.check_mode:
            if self.action_type == "assign":
                msg = f"Reserved IPv6 {self.ip} would be assigned to Droplet {self.droplet_id}"
            else:
                msg = f"Reserved IPv6 {self.ip} would be unassigned"
            self.module.exit_json(
                changed=True,
                msg=msg,
                action={},
            )
        else:
            self.perform_action()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        ip=dict(type="str", required=True),
        type=dict(type="str", required=True, choices=["assign", "unassign"]),
        droplet_id=dict(type="int", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("type", "assign", ["droplet_id"]),
        ],
    )
    ReservedIPv6Action(module)


if __name__ == "__main__":
    main()
