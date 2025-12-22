#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: apps_info

short_description: List all App Platform applications on your account

version_added: 0.6.0

description:
  - List all App Platform applications on your account.
  - |
    App Platform is a Platform-as-a-Service (PaaS) offering that allows
    developers to publish code directly to DigitalOcean servers without
    worrying about the underlying infrastructure.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Apps).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get all App Platform applications
  digitalocean.cloud.apps_info:
    token: "{{ token }}"
"""


RETURN = r"""
apps:
  description: App Platform applications.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      spec:
        name: my-app
        region: nyc
        services:
          - name: web
            github:
              repo: my-org/my-repo
              branch: main
      default_ingress: https://my-app-xxxxx.ondigitalocean.app
      created_at: '2020-03-13T19:20:47.442049222Z'
      updated_at: '2020-03-13T19:20:47.442049222Z'
      active_deployment:
        id: deployment-id
        phase: ACTIVE
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Apps result information.
  returned: always
  type: str
  sample:
    - Current apps
    - No apps
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class AppsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        apps = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.apps,
            meth="list",
            key="apps",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if apps:
            self.module.exit_json(
                changed=False,
                msg="Current apps",
                apps=apps,
            )
        self.module.exit_json(changed=False, msg="No apps", apps=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    AppsInformation(module)


if __name__ == "__main__":
    main()
