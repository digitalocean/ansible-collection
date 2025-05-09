#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplet

short_description: Create or delete Droplets

version_added: 0.2.0

description:
  - Creates or deletes Droplets.
  - View the create API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/droplets_create).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The human-readable string you wish to use when displaying the Droplet name.
      - |
        The name, if set to a domain name managed in the DigitalOcean DNS management system,
        will configure a PTR record for the Droplet.
      - |
        The name set during creation will also determine the hostname for the Droplet
        in its internal configuration.
    type: str
    required: false
  droplet_id:
    description:
      - |
        The Droplet ID which can be used for C(state=absent) when there are more than
        one Droplet with the same name within the same region
    type: int
    required: false
  region:
    description:
      - The slug identifier for the region that you wish to deploy the Droplet in.
      - |
        If the specific datacenter is not important, a slug prefix (e.g. C(nyc)) can be
        used to deploy the Droplet in any of the that region's locations (C(nyc1), C(nyc2),
        or nyc3).
      - If the region is omitted from the create request completely, the Droplet may
        deploy in any region.
    type: str
    required: false
  size:
    description:
      - The slug identifier for the size that you wish to select for this Droplet.
      - Required if C(state=present).
      - If C(resize) is set to C(true), this will be the new size of the Droplet.
      - If C(resize_disk) is also set to C(true), this will be the new size of the Droplet disk.
    type: str
    required: false
  resize:
    description:
      - Resize the Droplet to a larger size if C(size) is larger than the current size.
      - If a permanent resize with disk changes included is desired, set the C(resize_disk) attribute to C(true).
    type: bool
    required: false
    default: false
  resize_disk:
    description:
      - Resize the Droplet to a larger size if C(size) is larger than the current size.
      - If a permanent resize with disk changes included is desired, set this attribute to C(true).
    type: bool
    required: false
    default: false
  image:
    description:
      - The image ID of a public or private image or the slug identifier for a public image.
      - This image will be the base image for your Droplet.
    type: str
    required: false
  ssh_keys:
    description:
      - |
        An array containing the IDs or fingerprints of the SSH keys that you wish to embed
        in the Droplet's root account upon creation.
    type: list
    elements: str
    required: false
    default: []
  backups:
    description:
      - A boolean indicating whether automated backups should be enabled for the Droplet.
    type: bool
    required: false
    default: false
  ipv6:
    description:
      - A boolean indicating whether to enable IPv6 on the Droplet.
    type: bool
    required: false
    default: false
  monitoring:
    description:
      - A boolean indicating whether to install the DigitalOcean agent for monitoring.
    type: bool
    required: false
    default: false
  tags:
    description:
      - A flat array of tag names as strings to apply to the Droplet after it is created.
      - Tag names can either be existing or new tags.
    type: list
    elements: str
    required: false
    default: []
  user_data:
    description:
      - |
        A string containing 'user data' which may be used to configure the Droplet on first boot,
        often a 'cloud-config' file or Bash script.
      - It must be plain text and may not exceed 64 KiB in size.
    type: str
    required: false
  volumes:
    description:
      - |
        An array of IDs for block storage volumes that will be attached to the Droplet
        once created.
      - The volumes must not already be attached to an existing Droplet.
    type: list
    elements: str
    required: false
    default: []
  vpc_uuid:
    description:
      - A string specifying the UUID of the VPC to which the Droplet will be assigned.
      - If excluded, the Droplet will be assigned to your account's default VPC for the region.
    type: str
    required: false
  with_droplet_agent:
    description:
      - |
        A boolean indicating whether to install the DigitalOcean agent used for providing
        access to the Droplet web console in the control panel.
      - By default, the agent is installed on new Droplets but installation errors
        (i.e. OS not supported) are ignored.
      - To prevent it from being installed, set to C(false).
      - To make installation errors fatal, explicitly set it to C(true).
    type: bool
    required: false
    default: false
  unique_name:
    description:
      - |
        When C(true) for C(state=present) the Droplet will only be created if it is uniquely
        named in the region and the region is specified.
      - |
        When C(true) for C(state=absent) the Droplet will only be destroyed if it is uniquely
        named in the region and the region is specified.
    type: bool
    required: false
    default: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create Droplet
  digitalocean.cloud.droplet:
    token: "{{ token }}"
    state: present
    name: example.com
    region: nyc3
    size: s-1vcpu-1gb
    image: ubuntu-20-04-x64
"""


RETURN = r"""
droplet:
  description: Droplet information.
  returned: always
  type: dict
  sample:
    droplet:
      id: 3164444
      name: example.com
      memory: 1024
      vcpus: 1
      disk: 25
      locked: false
      status: new
      kernel:
      created_at: '2020-07-21T18:37:44Z'
      features:
      - backups
      - private_networking
      - ipv6
      - monitoring
      backup_ids: []
      next_backup_window:
      snapshot_ids: []
      image:
        id: 63663980
        name: 20.04 (LTS) x64
        distribution: Ubuntu
        slug: ubuntu-20-04-x64
        public: true
        regions:
        - ams2
        - ams3
        - blr1
        - fra1
        - lon1
        - nyc1
        - nyc2
        - nyc3
        - sfo1
        - sfo2
        - sfo3
        - sgp1
        - tor1
        created_at: '2020-05-15T05:47:50Z'
        type: snapshot
        min_disk_size: 20
        size_gigabytes: 2.36
        description: ''
        tags: []
        status: available
        error_message: ''
      volume_ids: []
      size:
        slug: s-1vcpu-1gb
        memory: 1024
        vcpus: 1
        disk: 25
        transfer: 1
        price_monthly: 5
        price_hourly: 0.00743999984115362
        regions:
        - ams2
        - ams3
        - blr1
        - fra1
        - lon1
        - nyc1
        - nyc2
        - nyc3
        - sfo1
        - sfo2
        - sfo3
        - sgp1
        - tor1
        available: true
        description: Basic
      size_slug: s-1vcpu-1gb
      networks:
        v4: []
        v6: []
      region:
        name: New York 3
        slug: nyc3
        features:
        - private_networking
        - backups
        - ipv6
        - metadata
        - install_agent
        - storage
        - image_transfer
        available: true
        sizes:
        - s-1vcpu-1gb
        - s-1vcpu-2gb
        - s-1vcpu-3gb
        - s-2vcpu-2gb
        - s-3vcpu-1gb
        - s-2vcpu-4gb
        - s-4vcpu-8gb
        - s-6vcpu-16gb
        - s-8vcpu-32gb
        - s-12vcpu-48gb
        - s-16vcpu-64gb
        - s-20vcpu-96gb
        - s-24vcpu-128gb
        - s-32vcpu-192g
      tags:
      - web
      - env:prod
    links:
      actions:
      - id: 7515
        rel: create
        href: https://api.digitalocean.com/v2/actions/7515
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Droplet result information.
  returned: always
  type: str
  sample:
    - Created Droplet example.com (11223344) in nyc3
    - Created Droplet example.com (11223344) in nyc3 is not 'active', it is 'new'
    - Deleted Droplet example.com (11223344) in nyc3
    - Deleting Droplet example.com (11223344) in nyc3 has failed
    - Droplet example.com in nyc3 would be created
    - Droplet example.com (11223344) in nyc3 exists
    - 'There are currently 2 Droplets named example.com in nyc3: 11223344, 55667788'
    - Droplet example.com in nyc3 would be created
    - Droplet example.com not found
    - Droplet example.com (11223344) in nyc3 would be deleted
    - Must provide droplet_id when deleting Droplets without unique_name
    - Droplet with ID 11223344 not found
    - Droplet with ID 11223344 would be deleted
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
    DigitalOceanConstants,
)
from ansible_collections.digitalocean.cloud.plugins.module_utils.droplet_resize import (
    DropletResize,
)


class Droplet(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.timeout = module.params.get("timeout")
        self.name = module.params.get("name")
        self.droplet_id = module.params.get("droplet_id")
        self.region = module.params.get("region")
        self.size = module.params.get("size")
        self.image = module.params.get("image")
        self.ssh_keys = module.params.get("ssh_keys")
        self.backups = module.params.get("backups")
        self.ipv6 = module.params.get("ipv6")
        self.monitoring = module.params.get("monitoring")
        self.resize = module.params.get("resize")
        self.resize_disk = module.params.get("resize_disk")
        self.tags = module.params.get("tags")
        self.user_data = module.params.get("user_data")
        self.volumes = module.params.get("volumes")
        self.vpc_uuid = module.params.get("vpc_uuid")
        self.with_droplet_agent = module.params.get("with_droplet_agent")
        self.unique_name = module.params.get("unique_name")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_droplets_by_name_and_region(self):
        droplets = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.droplets,
            meth="list",
            key="droplets",
            params=dict(name=self.name),
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        # NOTE: DigitalOcean Droplet names are not required to be unique!
        found_droplets = []
        for droplet in droplets:
            droplet_name = droplet.get("name")
            if droplet_name == self.name:
                droplet_region = droplet.get("region")
                if droplet_region:
                    droplet_region_slug = droplet_region.get("slug")
                    if droplet_region_slug == self.region:
                        found_droplets.append(droplet)
        return found_droplets

    def get_droplet_by_id(self, droplet_id):
        try:
            droplet_get = self.client.droplets.get(droplet_id=droplet_id)
            droplet = droplet_get.get("droplet")
            if droplet:
                return droplet
            return None
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
                droplet=[],
            )

    def create_droplet(self):
        try:
            body = {
                "name": self.name,
                "region": self.region,
                "size": self.size,
                "image": self.image,
                "ssh_keys": self.ssh_keys,
                "backups": self.backups,
                "ipv6": self.ipv6,
                "monitoring": self.monitoring,
                "tags": self.tags,
                "user_data": self.user_data,
                "volumes": self.volumes,
                "vpc_uuid": self.vpc_uuid,
                "with_droplet_agent": self.with_droplet_agent,
            }
            if self.module_override_options:
                body.update(self.module_override_options)

            droplet = self.client.droplets.create(body=body)["droplet"]

            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and droplet["status"] != "active":
                time.sleep(DigitalOceanConstants.SLEEP)
                droplet["status"] = self.get_droplet_by_id(droplet["id"])["status"]

            if droplet["status"] != "active":
                self.module.fail_json(
                    changed=True,
                    msg=(
                        f"Created Droplet {droplet['name']} ({droplet['id']}) in {droplet['region']['slug']}"
                        f" is not 'active', it is '{droplet['status']}'"
                    ),
                    droplet=droplet,
                )

            self.module.exit_json(
                changed=True,
                msg=f"Created Droplet {droplet['name']} ({droplet['id']}) in {droplet['region']['slug']}",
                droplet=droplet,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, droplet=[]
            )

    def delete_droplet(self, droplet):
        try:
            droplet_id = droplet["id"]
            droplet_name = droplet["name"]
            droplet_region = droplet["region"]["slug"]
            self.client.droplets.destroy(droplet_id=droplet_id)

            # Ensure Droplet is deleted:
            # A successful request will receive a 204 status code with no body in response.
            # This indicates that the request was processed successfully.
            droplet_still_exists = self.get_droplet_by_id(droplet_id)
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and droplet_still_exists:
                time.sleep(DigitalOceanConstants.SLEEP)
                droplet_still_exists = self.get_droplet_by_id(droplet_id)

            if droplet_still_exists:
                self.module.fail_json(
                    changed=False,
                    msg=f"Deleting Droplet {droplet_name} ({droplet_id}) in {droplet_region} has failed",
                    droplet=droplet,
                )

            self.module.exit_json(
                changed=True,
                msg=f"Deleted Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
                droplet=droplet,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, droplet=[]
            )

    def present(self):
        if self.unique_name:
            droplets = self.get_droplets_by_name_and_region()
            if len(droplets) == 0:
                if self.module.check_mode:
                    self.module.exit_json(
                        changed=True,
                        msg=f"Droplet {self.name} in {self.region} would be created",
                        droplet=[],
                    )
                else:
                    self.create_droplet()

            elif len(droplets) == 1:
                self.droplet_id = droplets[0]["id"]

                if self.module.params.get("resize"):
                    if not self.droplet_id:
                        self.module.fail_json(
                            changed=False,
                            msg="Unable to find Droplet ID for resize",
                        )

                    droplet = self.get_droplet_by_id(self.droplet_id)
                    if not droplet:
                        self.module.fail_json(
                            changed=False,
                            msg=f"Droplet with ID {self.droplet_id} not found",
                        )

                    self.current_size = droplet["size"]["slug"]
                    self.new_size = self.size

                    if self.current_size == self.size:
                        self.module.exit_json(
                            changed=False,
                            msg=f"Droplet {droplet['name']} ({self.droplet_id}) is already size {self.new_size}",
                            droplet=droplet,
                        )

                    if self.module.check_mode:
                        self.module.exit_json(
                            changed=True,
                            msg=f"Droplet {droplet['name']} ({self.droplet_id}) would be resized to size {self.new_size}",
                            droplet=droplet,
                        )

                    resize_action = DropletResize(
                        module=self.module,
                        droplet_id=self.droplet_id,
                        region=self.region,
                        current_size=self.current_size,
                        new_size=self.new_size,
                        resize_disk=self.resize_disk,
                    )
                    resize_action.resize_droplet()

                self.module.exit_json(
                    changed=False,
                    msg=f"Droplet {self.name} ({droplets[0]['id']}) in {self.region} exists",
                    droplet=droplets[0],
                )

            elif len(droplets) > 1:
                droplet_ids = ", ".join([str(droplet["id"]) for droplet in droplets])
                self.module.fail_json(
                    changed=False,
                    msg=f"There are currently {len(droplets)} Droplets named {self.name} in {self.region}: {droplet_ids}",
                    droplet=[],
                )

        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Droplet {self.name} in {self.region} would be created",
                droplet=[],
            )
        else:
            self.create_droplet()

    def absent(self):
        if self.unique_name:
            droplets = self.get_droplets_by_name_and_region()
            if len(droplets) == 0:
                if self.module.check_mode:
                    self.module.exit_json(
                        changed=False,
                        msg=f"Droplet {self.name} in {self.region} not found",
                        droplet=[],
                    )
                else:
                    self.module.exit_json(
                        changed=False,
                        msg=f"Droplet {self.name} in {self.region} not found",
                        droplet=[],
                    )
            elif len(droplets) == 1:
                if self.module.check_mode:
                    self.module.exit_json(
                        changed=True,
                        msg=f"Droplet {self.name} ({droplets[0]['id']}) in {self.region} would be deleted",
                        droplet=droplets[0],
                    )
                else:
                    self.delete_droplet(droplets[0])
            elif len(droplets) > 1:
                droplet_ids = ", ".join([str(droplet["id"]) for droplet in droplets])
                self.module.fail_json(
                    changed=False,
                    msg=f"There are currently {len(droplets)} Droplets named {self.name} in {self.region}: {droplet_ids}",
                    droplet=[],
                )

        if not self.droplet_id:
            self.module.fail_json(
                changed=False,
                msg="Must provide droplet_id when deleting Droplets without unique_name",
                droplet=[],
            )

        droplet = self.get_droplet_by_id(self.droplet_id)
        if not droplet:
            self.module.exit_json(
                changed=False,
                msg=f"Droplet with ID {self.droplet_id} not found",
                droplet=[],
            )
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Droplet with ID {self.droplet_id} would be deleted",
                droplet=droplet,
            )
        else:
            self.delete_droplet(droplet)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        droplet_id=dict(type="int", required=False),
        region=dict(type="str", required=False),
        size=dict(type="str", required=False),
        image=dict(type="str", required=False),
        ssh_keys=dict(
            type="list", elements="str", required=False, default=[], no_log=True
        ),
        backups=dict(type="bool", required=False, default=False),
        ipv6=dict(type="bool", required=False, default=False),
        monitoring=dict(type="bool", required=False, default=False),
        resize=dict(type="bool", required=False, default=False),
        resize_disk=dict(type="bool", required=False, default=False),
        tags=dict(type="list", elements="str", required=False, default=[]),
        user_data=dict(type="str", required=False),
        volumes=dict(type="list", elements="str", required=False, default=[]),
        vpc_uuid=dict(type="str", required=False),
        with_droplet_agent=dict(type="bool", required=False, default=False),
        unique_name=dict(type="bool", required=False, default=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "present", ("name", "size", "image")),
        ],
        required_by={
            "unique_name": "region",
            "resize_disk": "resize",
        },
    )
    Droplet(module)


if __name__ == "__main__":
    main()
