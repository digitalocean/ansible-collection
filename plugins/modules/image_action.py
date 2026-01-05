#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: image_action

short_description: Perform actions on images

version_added: 1.9.0

description:
  - Perform actions on images such as transfer and convert.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Image-Actions).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  image_id:
    description:
      - The unique identifier of the image.
    type: int
    required: true
  type:
    description:
      - The type of action to perform.
    type: str
    required: true
    choices:
      - transfer
      - convert
  region:
    description:
      - The slug identifier for the region to transfer the image to.
      - Required when type is C(transfer).
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Transfer image to another region
  digitalocean.cloud.image_action:
    token: "{{ token }}"
    image_id: 12345678
    type: transfer
    region: sfo2

- name: Convert image to snapshot
  digitalocean.cloud.image_action:
    token: "{{ token }}"
    image_id: 12345678
    type: convert
"""


RETURN = r"""
action:
  description: Image action information.
  returned: always
  type: dict
  sample:
    id: 12345678
    status: in-progress
    type: transfer
    started_at: '2020-03-13T19:20:47.442049222Z'
    completed_at: null
    resource_id: 7555620
    resource_type: image
    region:
      name: San Francisco 2
      slug: sfo2
      sizes: []
      features: []
      available: true
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Image action result information.
  returned: always
  type: str
  sample:
    - Initiated transfer action on image
    - Initiated convert action on image
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanConstants,
)


class ImageAction(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.image_id = module.params.get("image_id")
        self.action_type = module.params.get("type")
        self.region = module.params.get("region")

        if self.state == "present":
            self.present()

    def perform_action(self):
        try:
            body = {
                "type": self.action_type,
            }

            if self.action_type == "transfer":
                if not self.region:
                    self.module.fail_json(
                        changed=False,
                        msg="region is required for transfer action",
                        action={},
                    )
                body["region"] = self.region

            action = self.client.image_actions.post(image_id=self.image_id, body=body)[
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
                        msg=f"Image {self.action_type} action failed",
                        action=action,
                    )
                time.sleep(DigitalOceanConstants.SLEEP)
                action = self.get_action_by_id(action["id"])

            self.module.exit_json(
                changed=True,
                msg=f"Completed {self.action_type} action on image {self.image_id}",
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
            self.module.exit_json(
                changed=True,
                msg=f"Image {self.action_type} action would be performed on {self.image_id}",
                action={},
            )
        else:
            self.perform_action()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        image_id=dict(type="int", required=True),
        type=dict(type="str", required=True, choices=["transfer", "convert"]),
        region=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("type", "transfer", ["region"]),
        ],
    )
    ImageAction(module)


if __name__ == "__main__":
    main()
