#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: spaces_key

short_description: Create or delete Spaces access keys

version_added: 1.9.0

description:
  - Create or delete Spaces access keys.
  - |
    Spaces access keys are used to authenticate with DigitalOcean Spaces,
    the S3-compatible object storage service.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Spaces-Keys).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The name of the Spaces access key.
    type: str
    required: true
  grants:
    description:
      - The grants for the Spaces access key.
      - Specifies which buckets and permissions the key has.
    type: list
    elements: dict
    required: false
    suboptions:
      bucket:
        description:
          - The bucket name the grant applies to.
        type: str
      permission:
        description:
          - The permission level.
        type: str
        choices:
          - read
          - readwrite
          - fullaccess
  access_key:
    description:
      - The access key ID.
      - Used for lookup when deleting.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create Spaces access key
  digitalocean.cloud.spaces_key:
    token: "{{ token }}"
    state: present
    name: my-spaces-key
    grants:
      - bucket: my-bucket
        permission: readwrite

- name: Delete Spaces access key
  digitalocean.cloud.spaces_key:
    token: "{{ token }}"
    state: absent
    name: my-spaces-key
    access_key: AKIAIOSFODNN7EXAMPLE
"""


RETURN = r"""
spaces_key:
  description: Spaces access key information.
  returned: always
  type: dict
  sample:
    name: my-spaces-key
    access_key: AKIAIOSFODNN7EXAMPLE
    secret_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
    grants:
      - bucket: my-bucket
        permission: readwrite
    created_at: '2020-03-13T19:20:47.442049222Z'
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Spaces access key result information.
  returned: always
  type: str
  sample:
    - Created Spaces access key my-spaces-key
    - Deleted Spaces access key my-spaces-key
    - Spaces access key my-spaces-key would be created
    - Spaces access key my-spaces-key exists
    - Spaces access key my-spaces-key does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class SpacesKey(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.grants = module.params.get("grants")
        self.access_key = module.params.get("access_key")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_spaces_keys(self):
        try:
            spaces_keys = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.spaces_keys,
                meth="list",
                key="keys",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            found_keys = []
            for key in spaces_keys:
                if self.name == key.get("name"):
                    found_keys.append(key)
                elif self.access_key and self.access_key == key.get("access_key"):
                    found_keys.append(key)
            return found_keys
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
                spaces_key={},
            )

    def create_spaces_key(self):
        try:
            body = {
                "name": self.name,
            }
            if self.grants:
                body["grants"] = self.grants

            spaces_key = self.client.spaces_keys.create(body=body)["key"]

            self.module.exit_json(
                changed=True,
                msg=f"Created Spaces access key {self.name}",
                spaces_key=spaces_key,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, spaces_key={}
            )

    def delete_spaces_key(self, spaces_key):
        try:
            self.client.spaces_keys.delete(access_key=spaces_key["access_key"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted Spaces access key {self.name}",
                spaces_key=spaces_key,
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
                spaces_key={},
            )

    def present(self):
        spaces_keys = self.get_spaces_keys()
        if len(spaces_keys) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Spaces access key {self.name} would be created",
                    spaces_key={},
                )
            else:
                self.create_spaces_key()
        elif len(spaces_keys) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Spaces access key {self.name} exists",
                spaces_key=spaces_keys[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(spaces_keys)} Spaces access keys named {self.name}",
                spaces_key={},
            )

    def absent(self):
        spaces_keys = self.get_spaces_keys()
        if len(spaces_keys) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Spaces access key {self.name} does not exist",
                spaces_key={},
            )
        elif len(spaces_keys) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Spaces access key {self.name} would be deleted",
                    spaces_key=spaces_keys[0],
                )
            else:
                self.delete_spaces_key(spaces_key=spaces_keys[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(spaces_keys)} Spaces access keys named {self.name}",
                spaces_key={},
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        grants=dict(type="list", elements="dict", required=False),
        access_key=dict(type="str", required=False, no_log=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    SpacesKey(module)


if __name__ == "__main__":
    main()
