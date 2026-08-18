#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: tags_info

short_description: List all of the tags on your account

version_added: 0.2.0

description:
  - List all of the tags on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/tags_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get tags
  digitalocean.cloud.tags_info:
    token: "{{ token }}"
"""


RETURN = r"""
tags:
  description: Tags.
  returned: always
  type: list
  elements: dict
  sample: []
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Tag result information.
  returned: always
  type: str
  sample:
    - Current tags
    - No tags
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanFunctions,
    DigitalOceanOptions,
)


class TagsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        tags = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.tags,
            meth="list",
            key="tags",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if tags:
            self.module.exit_json(
                changed=False,
                msg="Current tags",
                tags=tags,
            )
        self.module.exit_json(changed=False, msg="No tags", tags=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    TagsInformation(module)


if __name__ == "__main__":
    main()
