#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: spaces_info

short_description: List all of the Spaces in your account

version_added: 0.5.0

description:
  - List all of the Spaces in your account.
  - View the documentation at U(https://www.digitalocean.com/products/spaces).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1
  - boto3 >= 1.28.57

options:
  name:
    description:
      - The short name of the Space to list.
      - If not provided all the Spaces in C(region) will be returned.
      - |
        For example, given C(name=my-do-space) and C(region=nyc3), the managed
        Space will be U(https://my-do-space.nyc3.digitaloceanspace.com).
    required: false
    type: str
  region:
    description:
      - The region in which to list Spaces.
      - The C(SPACES_REGION) environment variable will be used.
    required: false
    type: str
  aws_access_key_id:
    description:
      - The AWS_ACCESS_KEY_ID to use for authentication.
      - The C(AWS_ACCESS_KEY_ID) environment variable will be used.
    required: false
    type: str
  aws_secret_access_key:
    description:
      - The AWS_SECRET_ACCESS_KEY to use for authentication.
      - The C(AWS_SECRET_ACCESS_KEY) environment variable will be used.
    required: false
    type: str

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get all Spaces in nyc3
  digitalocean.cloud.spaces_info:
    aws_access_key_id: "{{ aws_access_key_id}}"
    aws_secret_access_key: "{{ aws_secret_access_key}}"
    region: "nyc3"

- name: Get Space my-do-space in nyc3
  digitalocean.cloud.spaces_info:
    aws_access_key_id: "{{ aws_access_key_id}}"
    aws_secret_access_key: "{{ aws_secret_access_key}}"
    name: "my-do-space"
    region: "nyc3"
"""


RETURN = r"""
spaces:
  description: Current spaces.
  returned: always
  type: list
  elements: dict
  sample:
    endpoint_url: https://nyc3.digitaloceanspaces.com
    name: my-do-space
    region: nyc3
    space_url: https://my-do-space.nyc3.digitaloceanspaces.com
error:
  description: DigitalOcean Spaces boto response metadata.
  returned: failure
  type: dict
  sample:
    RequestId: 1234567890ABCDEF
    HostId: Host ID data as a hash
    HTTPStatusCode: 400
    HTTPHeaders: Header metadata key/values
    RetryAttempts': 0
msg:
  description: Spaces result information.
  returned: always
  type: str
  sample:
    - Current Spaces in nyc3
    - Existing Space named my-do-space in nyc3
    - No Spaces in sfo3
    - No Space named my-do-space in nyc3
    - Failed to list Spaces in nyc3
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import env_fallback
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)
from ansible_collections.digitalocean.cloud.plugins.module_utils.spaces import Spaces


class SpacesInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.region = module.params.get("region")
        self.aws_access_key_id = module.params.get("aws_access_key_id")
        self.aws_secret_access_key = module.params.get("aws_secret_access_key")
        self.spaces = Spaces(module)
        if self.state == "present":
            self.present()

    def present(self):
        spaces = self.spaces.get()
        if spaces:
            if self.name:
                self.module.exit_json(
                    changed=False,
                    msg=f"Existing Space named {self.name} in {self.region}",
                    spaces=spaces,
                )
            self.module.exit_json(
                changed=False, msg=f"Current Spaces in {self.region}", spaces=spaces
            )

        if self.name:
            self.module.exit_json(
                changed=False,
                msg=f"No Space named {self.name} in {self.region}",
                spaces=spaces,
            )
        self.module.exit_json(
            changed=False, msg=f"No Spaces in {self.region}", spaces=spaces
        )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        region=dict(
            type="str", fallback=(env_fallback, ["SPACES_REGION"]), required=False
        ),
        aws_access_key_id=dict(
            type="str",
            fallback=(
                env_fallback,
                [
                    "AWS_ACCESS_KEY_ID",
                ],
            ),
            required=False,
        ),
        aws_secret_access_key=dict(
            type="str",
            fallback=(
                env_fallback,
                [
                    "AWS_SECRET_ACCESS_KEY",
                ],
            ),
            no_log=True,
            required=False,
        ),
        client_override_options=dict(type="dict", required=False),
        module_override_options=dict(type="dict", required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    SpacesInformation(module)


if __name__ == "__main__":
    main()
