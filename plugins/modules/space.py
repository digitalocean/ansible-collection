#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: space

short_description: Manage Spaces

version_added: 0.5.0

description:
  - Manage Spaces.
  - View the documentation at U(https://www.digitalocean.com/products/spaces).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1
  - boto3 >= 1.28.53

options:
  name:
    description:
      - The short name of the Space to create or delete.
      - |
        For example, given C(name=my-do-space) and C(region=nyc3), the managed
        Space will be U(https://my-do-space.nyc3.digitaloceanspace.com).
    required: true
    type: str
  region:
    description:
      - The region in which to create or delete the Space.
      - The C(SPACES_REGION) environment variable will be used.
    required: true
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
- name: Create Space my-do-space in nyc3
  digitalocean.cloud.space:
    state: present
    name: my-do-space
    region: nyc3
    aws_access_key_id: "{{ aws_access_key_id}}"
    aws_secret_access_key: "{{ aws_secret_access_key}}"
"""


RETURN = r"""
spaces:
  description: Current spaces.
  returned: always
  type: dict
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
  description: Space result information.
  returned: always
  type: str
  sample:
    - Created Space named my-do-space in nyc3
    - Failed to create Space named my-do-space in nyc3
    - No Spaces named my-do-space in nyc3, would create
    - Existing Space named my-do-space in nyc3, would create
    - Deleted Space named my-do-space in nyc3
    - Failed to delete Space named my-do-space in nyc3
    - Existing Space named my-do-space in nyc3, would delete
    - Failed to list Spaces in nyc3
"""

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.basic import env_fallback
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)
from ansible_collections.digitalocean.cloud.plugins.module_utils.spaces import Spaces


class Space(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.region = module.params.get("region")
        self.aws_access_key_id = module.params.get("aws_access_key_id")
        self.aws_secret_access_key = module.params.get("aws_secret_access_key")
        self.spaces = Spaces(module)
        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def create(self):
        spaces = self.spaces.create()

        self.module.exit_json(
            changed=True,
            msg=f"Created Space named {self.name} in {self.region}",
            spaces=spaces,
        )

    def delete(self):
        self.spaces.delete()

        self.module.exit_json(
            changed=True,
            msg=f"Deleted Space named {self.name} in {self.region}",
            spaces=[],
        )

    def present(self):
        spaces = self.spaces.get()

        if len(spaces) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"No Spaces named {self.name} in {self.region}, would create",
                    spaces=[],
                )
            self.create()

        elif len(spaces) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Existing Space named {self.name} in {self.region}",
                spaces=spaces,
            )

        self.module.fail_json(
            changed=False,
            msg=f"There are {len(spaces)} Spaces named {self.name} in {self.region}, this should not happen",
            spaces=spaces,
        )

    def absent(self):
        spaces = self.spaces.get()

        if len(spaces) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"No Spaces named {self.name} in {self.region}",
                spaces=[],
            )

        elif len(spaces) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Existing Space named {self.name} in {self.region}, would delete",
                    spaces=spaces[0],
                )
            self.delete()

        self.module.fail_json(
            changed=False,
            msg=f"There are {len(spaces)} Spaces named {self.name} in {self.region}, this should not happen",
            spaces=spaces,
        )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        region=dict(type="str", required=True),
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
    Space(module)


if __name__ == "__main__":
    main()
