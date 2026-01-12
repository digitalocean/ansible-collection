#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: floating_ip_action

short_description: Assign or unassign a floating IP to a Droplet (legacy)

version_added: 1.9.0

description:
  - Assign or unassign a floating IP to a Droplet.
  - |
    NOTE: Floating IPs have been renamed to Reserved IPs. This module is
    provided for backwards compatibility. New implementations should use
    the reserved_ip_assign module instead.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Floating-IP-Actions).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  ip:
    description:
      - The floating IP address.
    type: str
    required: true
  action:
    description:
      - The action to perform on the floating IP.
    type: str
    required: true
    choices:
      - assign
      - unassign
  droplet_id:
    description:
      - The ID of the Droplet to assign the floating IP to.
      - Required when action is assign.
    type: int
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Assign a floating IP to a Droplet
  digitalocean.cloud.floating_ip_action:
    token: "{{ token }}"
    ip: 192.0.2.1
    action: assign
    droplet_id: 12345678

- name: Unassign a floating IP from a Droplet
  digitalocean.cloud.floating_ip_action:
    token: "{{ token }}"
    ip: 192.0.2.1
    action: unassign
"""


RETURN = r"""
action:
  description: DigitalOcean action information.
  returned: always
  type: dict
  sample:
    id: 1882339039
    status: completed
    type: assign
    started_at: '2023-09-03T12:59:10Z'
    completed_at: '2023-09-03T12:59:15Z'
    resource_id: 192.0.2.1
    resource_type: floating_ip
    region:
      name: New York 3
      slug: nyc3
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Floating IP action result information.
  returned: always
  type: str
  sample:
    - Floating IP 192.0.2.1 assigned to Droplet 12345678
    - Floating IP 192.0.2.1 unassigned
    - Floating IP action would be performed
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanConstants,
)


class FloatingIPAction(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.timeout = module.params.get("timeout")
        self.ip = module.params.get("ip")
        self.action_type = module.params.get("action")
        self.droplet_id = module.params.get("droplet_id")

        if self.action_type == "assign":
            if not self.droplet_id:
                self.module.fail_json(
                    changed=False,
                    msg="droplet_id is required when action is assign",
                    action={},
                )
            self.assign()
        elif self.action_type == "unassign":
            self.unassign()

    def assign(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Floating IP {self.ip} would be assigned to Droplet {self.droplet_id}",
                action={},
            )

        try:
            body = {
                "type": "assign",
                "droplet_id": self.droplet_id,
            }
            action = self.client.reserved_ips_actions.post(
                reserved_ip=self.ip, body=body
            )["action"]
            action_id = action["id"]

            # Wait for the action to complete
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                status = action.get("status", "").lower()
                if status == "completed":
                    break
                if status == "errored":
                    self.module.fail_json(
                        changed=True,
                        msg=f"Floating IP {self.ip} assign action failed",
                        action=action,
                    )
                time.sleep(DigitalOceanConstants.SLEEP)
                action = self.get_floating_ip_action_by_id(action_id=action_id)

            if action.get("status", "").lower() != "completed":
                self.module.fail_json(
                    changed=True,
                    msg=f"Floating IP {self.ip} assign action did not complete within {self.timeout} seconds (current status: {action['status']})",
                    action=action,
                )

            self.module.exit_json(
                changed=True,
                msg=f"Floating IP {self.ip} assigned to Droplet {self.droplet_id}",
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

    def unassign(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Floating IP {self.ip} would be unassigned",
                action={},
            )

        try:
            body = {
                "type": "unassign",
            }
            action = self.client.reserved_ips_actions.post(
                reserved_ip=self.ip, body=body
            )["action"]
            action_id = action["id"]

            # Wait for the action to complete
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                status = action.get("status", "").lower()
                if status == "completed":
                    break
                if status == "errored":
                    self.module.fail_json(
                        changed=True,
                        msg=f"Floating IP {self.ip} unassign action failed",
                        action=action,
                    )
                time.sleep(DigitalOceanConstants.SLEEP)
                action = self.get_floating_ip_action_by_id(action_id=action_id)

            if action.get("status", "").lower() != "completed":
                self.module.fail_json(
                    changed=True,
                    msg=f"Floating IP {self.ip} unassign action did not complete within {self.timeout} seconds (current status: {action['status']})",
                    action=action,
                )

            self.module.exit_json(
                changed=True,
                msg=f"Floating IP {self.ip} unassigned",
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

    def get_floating_ip_action_by_id(self, action_id):
        try:
            action = self.client.reserved_ips_actions.get(
                reserved_ip=self.ip, action_id=action_id
            )["action"]
            return action
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


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        ip=dict(type="str", required=True),
        action=dict(type="str", required=True, choices=["assign", "unassign"]),
        droplet_id=dict(type="int", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("action", "assign", ("droplet_id",)),
        ],
    )
    FloatingIPAction(module)


if __name__ == "__main__":
    main()
