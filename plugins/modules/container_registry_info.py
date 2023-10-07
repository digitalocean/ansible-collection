#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: container_registry_info

short_description: Get information about your container registry

version_added: 0.5.0

description:
  - Get information about your container registry.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Container-Registry).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get container registry
  digitalocean.cloud.container_registry_info:
    token: "{{ token }}"
"""


RETURN = r"""
registry:
  description: Container registry information.
  returned: always
  type: dict
  sample:
    name: example
    created_at: "2020-03-21T16:02:37Z"
    region: fra1,
    storage_usage_bytes: 29393920
    storage_usage_bytes_updated_at: "2020-11-04T21:39:49.530562231Z"
    subscription:
      tier:
        name: Basic
        slug: basic
        included_repositories: 5
        included_storage_bytes: 5368709120
        allow_storage_overage: true
        included_bandwidth_bytes: 5368709120
        monthly_price_in_cents: 500
        storage_overage_price_in_cents: 2
      created_at: "2020-01-23T21:19:12Z"
      updated_at: "2020-11-05T15:53:24Z"
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Container registry result information.
  returned: always
  type: str
  sample:
    - Current container registry
    - No container registry
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class ContainerRegistryV2RepositoriesInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.registry_name = self.module.params.get("registry_name")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            registry = self.client.registry.get()
            if registry:
                self.module.exit_json(
                    changed=False,
                    msg="Current container registry",
                    registry=registry["registry"],
                )
            self.module.exit_json(
                changed=False, msg="No container registry", registry={}
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            if err.status_code == 404:  # Handle non-existent case gracefully
                self.module.exit_json(
                    changed=False, msg="No container registry", registry={}
                )
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, registry={}
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    ContainerRegistryV2RepositoriesInformation(module)


if __name__ == "__main__":
    main()
