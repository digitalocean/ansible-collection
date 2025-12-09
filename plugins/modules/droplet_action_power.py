#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplet_action_power

short_description: Set power states of a Droplet

version_added: 0.3.0

description:
  - Set power states of a Droplet.
  - State power_on powers on a Droplet.
  - |
    State power_off is a hard shutdown and should only be used if the shutdown
    action is not successful. It is similar to cutting the power on a server and
    could lead to complications.
  - |
    State shutdown is an attempt to shutdown the Droplet in a graceful way,
    similar to using the shutdown command from the console. Since a shutdown
    command can fail, this action guarantees that the command is issued, not that
    it succeeds. The preferred way to turn off a Droplet is to attempt a shutdown,
    with a reasonable timeout, followed by a power_off state to ensure the
    Droplet is off.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Droplet-Actions).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  droplet_id:
    description:
      - A unique identifier for a Droplet instance.
      - If provided, C(name) and C(region) are ignored.
    type: int
    required: false
  name:
    description:
      - The name of the Droplet to act on.
      - If provided, must be unique and given with C(region).
    type: str
    required: false
  region:
    description:
      - The name of the Droplet to act on.
      - Required with C(name).
    type: str
    required: false
  state:
    description:
      - The power state transition.
    type: str
    choices: [power_off, power_on, shutdown]
    default: power_on
  force_power_off:
    description:
      - Force power off if C(shutdown) fails.
    type: bool
    required: false
    default: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Power off a Droplet
  digitalocean.cloud.droplet_action_power:
    token: "{{ token }}"
    state: power_off
    id: 1122334455

- name: Power on a Droplet
  digitalocean.cloud.droplet_action_power:
    token: "{{ token }}"
    state: power_on
    id: 1122334455

- name: Shut down a Droplet
  digitalocean.cloud.droplet_action_power:
    token: "{{ token }}"
    state: shutdown
    id: 1122334455

- name: Shut down a Droplet (force if unsuccessful)
  digitalocean.cloud.droplet_action_power:
    token: "{{ token }}"
    state: shutdown
    force_power_off: true
    id: 1122334455
"""


RETURN = r"""
action:
  description: DigitalOcean action information.
  returned: always
  type: dict
  sample:
    completed_at: null
    id: 1882339039
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
      - and many more
      slug: nyc3
    region_slug: nyc3
    resource_id: 336851565
    resource_type: droplet
    started_at: '2023-09-03T12:59:10Z'
    status: in-progress
    type: power_on
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: DigitalOcean action information.
  returned: always
  type: str
  sample:
    - No Droplet with ID 336851565
    - No Droplet with name test-droplet-1 in nyc3
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'power_off'
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'power_off' and it has not completed, status is 'in-progress'
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'power_off' and it has not completed, status is 'errored'
    - Droplet test-droplet-1 (336851565) in nyc3 would be sent action 'power_off', it is 'off'
    - Droplet test-droplet-1 (336851565) in nyc3 would not be sent action 'power_off', it is 'active'
    - Droplet test-droplet-1 (336851565) in nyc3 not sent action 'power_off', it is 'off'
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'power_on'
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'power_on' and it has not completed, status is 'in-progress'
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'power_on' and it has not completed, status is 'errored'
    - Droplet test-droplet-1 (336851565) in nyc3 would be sent action 'power_on', it is 'active'
    - Droplet test-droplet-1 (336851565) in nyc3 would not be sent action 'power_on', it is 'off'
    - Droplet test-droplet-1 (336851565) in nyc3 not sent action 'power_on', it is 'active'
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'shutdown'
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'shutdown' and it has not completed, status is 'in-progress'
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'shutdown' and it has not completed, status is 'errored'
    - Droplet test-droplet-1 (336851565) in nyc3 would be sent action 'shutdown', it is 'active'
    - Droplet test-droplet-1 (336851565) in nyc3 would not be sent action 'shutdown', it is 'off'
    - Droplet test-droplet-1 (336851565) in nyc3 not sent action 'shutdown', it is 'off'
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
    DigitalOceanConstants,
)


class DropletActionPower(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.timeout = module.params.get("timeout")
        self.droplet_id = module.params.get("droplet_id")
        self.name = module.params.get("name")
        self.region = module.params.get("region")
        self.droplet = self.find_droplet()
        self.type = self.state
        self.force_power_off = module.params.get("force_power_off")
        if self.type == "power_off":
            self.power_off()
        elif self.type == "power_on":
            self.power_on()
        elif self.type == "shutdown":
            self.shutdown()

    def find_droplet(self):
        if self.droplet_id:
            try:
                droplet = self.client.droplets.get(droplet_id=self.droplet_id)[
                    "droplet"
                ]
                if droplet:
                    return droplet
                self.module.fail_json(
                    changed=False,
                    msg=f"No Droplet with ID {self.droplet_id}",
                    action=[],
                )
            except DigitalOceanCommonModule.HttpResponseError as err:
                error = {
                    "Message": err.error.message,
                    "Status Code": err.status_code,
                    "Reason": err.reason,
                }
                self.module.fail_json(
                    changed=False, msg=error.get("Message"), error=error, action=[]
                )
        elif self.name and self.region:
            droplets = DigitalOceanFunctions.get_droplet_by_name_in_region(
                module=self.module,
                client=self.client,
                region=self.region,
                name=self.name,
            )
            if len(droplets) == 0:
                self.module.fail_json(
                    changed=False,
                    msg=f"No Droplet named {self.name} in {self.region}",
                    action=[],
                )
            elif len(droplets) > 1:
                droplet_ids = ", ".join([str(droplet["id"]) for droplet in droplets])
                self.module.fail_json(
                    changed=False,
                    msg=f"There are currently {len(droplets)} Droplets named {self.name} in {self.region}: {droplet_ids}",
                    action=[],
                )
            return droplets[0]

        self.module.fail_json(
            changed=False,
            msg="Should not reach this",
            action=[],
        )

    def get_action_by_id(self, action_id):
        try:
            action = self.client.actions.get(action_id=action_id)["action"]
            return action
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, action=[]
            )

    def set_power_off(self):
        try:
            body = {
                "type": self.type,
            }
            action = self.client.droplet_actions.post(
                droplet_id=self.droplet["id"], body=body
            )["action"]

            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and action["status"] != "completed":
                time.sleep(DigitalOceanConstants.SLEEP)
                action = self.get_action_by_id(action_id=action["id"])

            if action["status"] != "completed":
                self.module.fail_json(
                    changed=True,
                    msg=(
                        f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']}"
                        f" sent action '{self.type}' and it has not completed, status is '{action['status']}'"
                    ),
                    action=action,
                )

            self.module.exit_json(
                changed=True,
                msg=f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} sent action '{self.type}'",
                action=action,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, action=[]
            )

    def set_power_on(self):
        try:
            body = {
                "type": self.type,
            }
            action = self.client.droplet_actions.post(
                droplet_id=self.droplet["id"], body=body
            )["action"]

            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and action["status"] != "completed":
                time.sleep(DigitalOceanConstants.SLEEP)
                action = self.get_action_by_id(action_id=action["id"])

            if action["status"] != "completed":
                self.module.fail_json(
                    changed=True,
                    msg=(
                        f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']}"
                        f" sent action '{self.type}' and it has not completed, status is '{action['status']}'"
                    ),
                    action=action,
                )

            self.module.exit_json(
                changed=True,
                msg=f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} sent action '{self.type}'",
                action=action,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, action=[]
            )

    def set_shutdown(self):
        try:
            body = {
                "type": self.type,
            }
            action = self.client.droplet_actions.post(
                droplet_id=self.droplet["id"], body=body
            )["action"]

            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and action["status"] != "completed":
                time.sleep(DigitalOceanConstants.SLEEP)
                action = self.get_action_by_id(action_id=action["id"])

            if action["status"] != "completed":
                if self.force_power_off:
                    self.power_off()

                self.module.fail_json(
                    changed=True,
                    msg=(
                        f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']}"
                        f" sent action '{self.type}' and it has not completed, status is '{action['status']}'"
                    ),
                    action=action,
                )

            self.module.exit_json(
                changed=True,
                msg=f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} sent action '{self.type}'",
                action=action,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, action=[]
            )

    def power_off(self):
        if self.module.check_mode:
            if self.droplet["status"] != "off":
                self.module.exit_json(
                    changed=True,
                    msg=(
                        f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} "
                        f"would be sent action '{self.type}', it is '{self.droplet['status']}'"
                    ),
                )
            self.module.exit_json(
                changed=False,
                msg=(
                    f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} "
                    f"would not be sent action '{self.type}', it is '{self.droplet['status']}'"
                ),
            )

        if self.droplet["status"] == "off":
            self.module.exit_json(
                changed=False,
                msg=(
                    f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} "
                    f"not sent action '{self.type}', it is '{self.droplet['status']}'"
                ),
            )

        self.set_power_off()

    def power_on(self):
        if self.module.check_mode:
            if self.droplet["status"] == "off":
                self.module.exit_json(
                    changed=True,
                    msg=(
                        f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} "
                        f"would be sent action '{self.type}', it is '{self.droplet['status']}'"
                    ),
                )
            self.module.exit_json(
                changed=False,
                msg=(
                    f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} "
                    f"would not be sent action '{self.type}', it is '{self.droplet['status']}'"
                ),
            )

        if self.droplet["status"] != "off":
            self.module.exit_json(
                changed=False,
                msg=(
                    f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} "
                    f"not sent action '{self.type}', it is '{self.droplet['status']}'"
                ),
            )

        self.set_power_on()

    def shutdown(self):
        if self.module.check_mode:
            if self.droplet["status"] != "off":
                self.module.exit_json(
                    changed=True,
                    msg=(
                        f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} "
                        f"would be sent action '{self.type}', it is '{self.droplet['status']}'"
                    ),
                )
            self.module.exit_json(
                changed=False,
                msg=(
                    f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} "
                    f"would not be sent action '{self.type}', it is '{self.droplet['status']}'"
                ),
            )

        if self.droplet["status"] == "off":
            self.module.exit_json(
                changed=False,
                msg=(
                    f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} "
                    f"not sent action '{self.type}', it is '{self.droplet['status']}'"
                ),
            )

        self.set_shutdown()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        droplet_id=dict(type="int", required=False),
        name=dict(type="str", required=False),
        region=dict(type="str", required=False),
        state=dict(
            type="str",
            choices=["power_off", "power_on", "shutdown"],
            default="power_on",
        ),
        force_power_off=dict(type="bool", required=False, default=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[("droplet_id", "name")],
        mutually_exclusive=[("droplet_id", "name")],
        required_together=[("name", "region")],
        required_if=[("state", "shutdown", ["force_power_off"])],
    )
    DropletActionPower(module)


if __name__ == "__main__":
    main()
