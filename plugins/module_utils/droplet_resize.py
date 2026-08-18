# -*- coding: utf-8 -*-
# Copyright: (c) 2025, DigitalOcean LLC <ansible-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


import time

from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanConstants,
)


class DropletResize(DigitalOceanCommonModule):
    def __init__(self, module, droplet_id, region, current_size, new_size, resize_disk):
        super().__init__(module)
        self.droplet_id = droplet_id
        self.current_size = current_size
        self.resize_disk = resize_disk
        self.new_size = new_size
        self.region = region
        self.type = "resize"
        self.timeout = module.params.get("timeout")

    def resize_droplet(self):
        try:
            body = {
                "type": "resize",
                "size": self.new_size,
                "disk": self.resize_disk,
            }

            # Capture the action response from the API
            action = self.client.droplet_actions.post(
                droplet_id=self.droplet_id, body=body
            )["action"]

            # Poll the action status until it completes
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and action["status"] != "completed":
                time.sleep(DigitalOceanConstants.SLEEP)
                action = self.get_action_by_id(action_id=action["id"])

            # Check if the action completed successfully
            if action["status"] != "completed":
                self.module.fail_json(
                    changed=True,
                    msg=(
                        f"Resize action for Droplet {self.droplet_id} from "
                        f"{self.current_size} to {self.new_size} has not completed, "
                        f"status is '{action['status']}'"
                    ),
                    action=action,
                )

            # Get the updated droplet information
            droplet = self.client.droplets.get(self.droplet_id)["droplet"]

            self.module.exit_json(
                changed=True,
                msg=f"Resized Droplet {droplet['name']} ({self.droplet_id}) in {self.region} from size {self.current_size} to size {self.new_size}",
                droplet=droplet,
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
