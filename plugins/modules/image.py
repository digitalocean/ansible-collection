#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: image

short_description: Manage custom images

version_added: 1.9.0

description:
  - Create, update, or delete custom images.
  - |
    Custom images allow you to create Droplets from your own disk images
    or import images from other cloud providers.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Images).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The display name for the image.
    type: str
    required: true
  url:
    description:
      - The URL from which the custom image will be imported.
      - Required when creating a new image.
    type: str
    required: false
  region:
    description:
      - The slug identifier for the region where the image will be available.
    type: str
    required: false
  distribution:
    description:
      - The name of the distribution for the image.
    type: str
    required: false
  description:
    description:
      - An optional description for the image.
    type: str
    required: false
  tags:
    description:
      - A list of tags to apply to the image.
    type: list
    elements: str
    required: false
  id:
    description:
      - The unique identifier of the image.
      - Used for lookup when updating or deleting.
    type: int
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create custom image from URL
  digitalocean.cloud.image:
    token: "{{ token }}"
    state: present
    name: my-custom-image
    url: https://example.com/my-image.qcow2
    region: nyc3
    distribution: Ubuntu
    description: My custom Ubuntu image

- name: Update image name
  digitalocean.cloud.image:
    token: "{{ token }}"
    state: present
    name: my-renamed-image
    id: 12345678

- name: Delete image
  digitalocean.cloud.image:
    token: "{{ token }}"
    state: absent
    name: my-custom-image
    id: 12345678
"""


RETURN = r"""
image:
  description: Image information.
  returned: always
  type: dict
  sample:
    id: 7555620
    name: my-custom-image
    distribution: Ubuntu
    slug: null
    public: false
    regions:
      - nyc3
    created_at: '2020-11-04T22:23:02Z'
    type: custom
    min_disk_size: 20
    size_gigabytes: 2.34
    description: My custom Ubuntu image
    tags: []
    status: available
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Image result information.
  returned: always
  type: str
  sample:
    - Created image my-custom-image
    - Updated image my-custom-image
    - Deleted image my-custom-image
    - Image my-custom-image would be created
    - Image my-custom-image exists
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
    DigitalOceanConstants,
)


class Image(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.url = module.params.get("url")
        self.region = module.params.get("region")
        self.distribution = module.params.get("distribution")
        self.description = module.params.get("description")
        self.tags = module.params.get("tags")
        self.id = module.params.get("id")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_images(self):
        try:
            images = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.images,
                meth="list",
                key="images",
                exc=DigitalOceanCommonModule.HttpResponseError,
                params={"private": True},
            )
            found_images = []
            for image in images:
                if self.name == image.get("name"):
                    found_images.append(image)
                elif self.id and self.id == image.get("id"):
                    found_images.append(image)
            return found_images
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
                image={},
            )

    def create_image(self):
        try:
            body = {
                "name": self.name,
                "url": self.url,
                "region": self.region,
            }
            if self.distribution:
                body["distribution"] = self.distribution
            if self.description:
                body["description"] = self.description
            if self.tags:
                body["tags"] = self.tags

            image = self.client.images.create_custom(body=body)["image"]

            # Wait for the image to become available
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                status = image.get("status", "").lower()
                if status == "available":
                    break
                if status == "deleted" or status == "error":
                    self.module.fail_json(
                        changed=True,
                        msg=f"Image creation failed with status: {status}",
                        image=image,
                    )
                time.sleep(DigitalOceanConstants.SLEEP)
                try:
                    image = self.client.images.get(image_id=image["id"])["image"]
                except DigitalOceanCommonModule.HttpResponseError:
                    pass

            self.module.exit_json(
                changed=True,
                msg=f"Created image {self.name} ({image['id']})",
                image=image,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, image={}
            )

    def update_image(self, image):
        try:
            body = {}
            if self.name:
                body["name"] = self.name
            if self.distribution:
                body["distribution"] = self.distribution
            if self.description:
                body["description"] = self.description

            updated_image = self.client.images.update(image_id=image["id"], body=body)[
                "image"
            ]

            self.module.exit_json(
                changed=True,
                msg=f"Updated image {self.name} ({updated_image['id']})",
                image=updated_image,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, image={}
            )

    def delete_image(self, image):
        try:
            self.client.images.delete(image_id=image["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted image {self.name} ({image['id']})",
                image=image,
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
                image={},
            )

    def present(self):
        images = self.get_images()
        if len(images) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Image {self.name} would be created",
                    image={},
                )
            else:
                if not self.url:
                    self.module.fail_json(
                        changed=False,
                        msg="url is required when creating an image",
                        image={},
                    )
                if not self.region:
                    self.module.fail_json(
                        changed=False,
                        msg="region is required when creating an image",
                        image={},
                    )
                self.create_image()
        elif len(images) == 1:
            # Check if update is needed
            if self.id:
                if self.module.check_mode:
                    self.module.exit_json(
                        changed=True,
                        msg=f"Image {self.name} ({images[0]['id']}) would be updated",
                        image=images[0],
                    )
                else:
                    self.update_image(images[0])
            else:
                self.module.exit_json(
                    changed=False,
                    msg=f"Image {self.name} ({images[0]['id']}) exists",
                    image=images[0],
                )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(images)} images named {self.name}",
                image={},
            )

    def absent(self):
        images = self.get_images()
        if len(images) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Image {self.name} does not exist",
                image={},
            )
        elif len(images) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Image {self.name} ({images[0]['id']}) would be deleted",
                    image=images[0],
                )
            else:
                self.delete_image(image=images[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(images)} images named {self.name}",
                image={},
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        url=dict(type="str", required=False),
        region=dict(type="str", required=False),
        distribution=dict(type="str", required=False),
        description=dict(type="str", required=False),
        tags=dict(type="list", elements="str", required=False),
        id=dict(type="int", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    Image(module)


if __name__ == "__main__":
    main()
