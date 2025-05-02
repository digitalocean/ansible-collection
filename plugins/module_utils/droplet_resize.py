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

            self.client.droplet_actions.post(droplet_id=self.droplet_id, body=body)

            # Wait for the resize action to complete
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                droplet = self.client.droplets.get(self.droplet_id)["droplet"]
                if droplet["size"]["slug"] == self.new_size:
                    self.module.exit_json(
                        changed=True,
                        msg=f"Resized Droplet {droplet['name']} ({self.droplet_id}) in {self.region} from size {self.current_size} to size {self.new_size}",
                        droplet=droplet,
                    )
                time.sleep(DigitalOceanConstants.SLEEP)

            self.module.fail_json(
                changed=False,
                msg=f"Resizing Droplet {self.droplet_id} from {self.current_size} to size {self.new_size} has failed",
            )
        except Exception as err:
            self.module.fail_json(
                changed=False,
                msg=f"An error occurred while resizing the Droplet: {str(err)}",
                error=str(err),
            )
