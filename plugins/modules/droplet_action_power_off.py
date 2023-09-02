#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplet_action_power_off

short_description: Power off a Droplet

version_added: 0.3.0

description:
  - Power off a Droplet.
  - A power_off event is a hard shutdown and should only be used if the shutdown action is not successful.
  - It is similar to cutting the power on a server and could lead to complications.
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

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Power off a Droplet
  digitalocean.cloud.droplet_action_power_off:
    token: "{{ token }}"
    state: present
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
    - Droplet test-droplet-1 (336851565) in nyc3 would be sent action 'power_off', it is 'off'
    - Droplet test-droplet-1 (336851565) in nyc3 would not be sent action 'power_off', it is 'active'
    - Droplet test-droplet-1 (336851565) in nyc3 not sent action 'power_off', it is 'off'
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
    DigitalOceanConstants,
)


class DropletActionPowerOff(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.type = "power_off"
        self.timeout = module.params.get("timeout")
        self.droplet_id = module.params.get("droplet_id")
        self.name = module.params.get("name")
        self.region = module.params.get("region")
        self.droplet = self.find_droplet()
        if self.state == "present":
            self.present()

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
                self.module.fail_json(
                    changed=False,
                    msg=f"Multiple Droplets ({len(droplets)}) named {self.name} found in {self.region}",
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

    def power_off(self):
        try:
            body = {
                "type": self.type,
            }
            action = self.client.droplet_actions.post(
                droplet_id=self.droplet["id"], body=body
            )["action"]

            status = action["status"]
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and status != "completed":
                time.sleep(DigitalOceanConstants.SLEEP)
                status = self.get_action_by_id(action_id=action["id"])["status"]

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

    def present(self):
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

        self.power_off()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        droplet_id=dict(type="int", required=False),
        name=dict(type="str", required=False),
        region=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[("droplet_id", "name")],
        mutually_exclusive=[("droplet_id", "name")],
        required_together=[("name", "region")],
    )
    DropletActionPowerOff(module)


if __name__ == "__main__":
    main()
