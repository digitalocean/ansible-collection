#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplet_action_resize

short_description: Resize a Droplet

version_added: 0.3.0

description:
  - Resize a Droplet.
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
  disk:
    description:
      - When true, the Droplet's disk will be resized in addition to its RAM and CPU.
      - This is a permanent change and cannot be reversed as a Droplet's disk size cannot be decreased.
    type: bool
    required: true
  size:
    description:
      - The slug identifier for the size to which you wish to resize the Droplet.
    type: str
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Resize a Droplet without resizing disk
  digitalocean.cloud.droplet_action_resize:
    token: "{{ token }}"
    state: present
    id: 1122334455
    disk: false
    size: s-2vcpu-4gb
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
    type: resize
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
    - Droplet test-droplet-1 (336851565) in nyc3 would be sent action 'resize', requested size is 's-2vcpu-4gb' and current size is 's-1vcpu-2gb'
    - Droplet test-droplet-1 (336851565) in nyc3 would not be sent action 'resize', requested size is 's-1vcpu-2gb' and current size is 's-1vcpu-2gb'
    - Droplet test-droplet-1 (336851565) in nyc3 not sent action 'resize', requested size is 's-2vcpu-4gb' and current size is 's-1vcpu-2gb'
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'resize', new size is 's-2vcpu-4gb'
    - Droplet test-droplet-1 (336851565) in nyc3 sent action 'resize' and it has not completed, status is 'in-progress'
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)
from ansible_collections.digitalocean.cloud.plugins.module_utils.droplet_resize import (
    DropletResize,
)


class DropletActionResize(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.type = "resize"
        self.timeout = module.params.get("timeout")
        self.droplet_id = module.params.get("droplet_id")
        self.name = module.params.get("name")
        self.region = module.params.get("region")
        self.disk = module.params.get("disk")
        self.size = module.params.get("size")
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

    def resize(self):
        try:
            dr = DropletResize(
                module=self.module,
                droplet_id=self.droplet["id"],
                new_size=self.size,
                resize_disk=self.disk,
            )
            dr.resize_droplet()
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
            if self.size != self.droplet["size"]["slug"]:
                self.module.exit_json(
                    changed=True,
                    msg=(
                        f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} "
                        f"would be sent action '{self.type}', requested size is '{self.size}' and current size is "
                        f"'{self.droplet['size']['slug']}'"
                    ),
                )
            self.module.exit_json(
                changed=False,
                msg=(
                    f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} would "
                    f"not be sent action '{self.type}', requested size is '{self.size}' and current size is "
                    f"'{self.droplet['size']['slug']}'"
                ),
            )

        if self.size == self.droplet["size"]["slug"]:
            self.module.exit_json(
                changed=False,
                msg=(
                    f"Droplet {self.droplet['name']} ({self.droplet['id']}) in {self.droplet['region']['slug']} not "
                    f"sent action '{self.type}', requested size is '{self.size}' and current size is "
                    f"'{self.droplet['size']['slug']}'"
                ),
            )

        self.resize()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        droplet_id=dict(type="int", required=False),
        name=dict(type="str", required=False),
        region=dict(type="str", required=False),
        disk=dict(type="bool", required=True),
        size=dict(type="str", required=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[("droplet_id", "name")],
        mutually_exclusive=[("droplet_id", "name")],
        required_together=[("name", "region")],
    )
    DropletActionResize(module)


if __name__ == "__main__":
    main()
