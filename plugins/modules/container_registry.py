#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: container_registry

short_description: Create or delete container registry

version_added: 1.9.0

description:
  - Create or delete your DigitalOcean container registry.
  - |
    DigitalOcean Container Registry is a private Docker image registry with
    additional tooling support that enables integration with your Docker
    environment and DigitalOcean Kubernetes clusters.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Container-Registry).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The name of the container registry.
      - Must be unique and contain only lowercase letters, numbers, and hyphens.
    type: str
    required: true
  subscription_tier_slug:
    description:
      - The slug of the subscription tier to use.
    type: str
    required: false
    choices:
      - starter
      - basic
      - professional
    default: basic
  region:
    description:
      - The slug of the region where the registry will be created.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create container registry
  digitalocean.cloud.container_registry:
    token: "{{ token }}"
    state: present
    name: my-registry
    subscription_tier_slug: basic
    region: nyc3

- name: Delete container registry
  digitalocean.cloud.container_registry:
    token: "{{ token }}"
    state: absent
    name: my-registry
"""


RETURN = r"""
registry:
  description: Container registry information.
  returned: always
  type: dict
  sample:
    name: my-registry
    created_at: "2020-03-21T16:02:37Z"
    region: nyc3
    storage_usage_bytes: 0
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
    - Created container registry my-registry
    - Deleted container registry my-registry
    - Container registry my-registry would be created
    - Container registry my-registry exists
    - Container registry does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class ContainerRegistry(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.subscription_tier_slug = module.params.get("subscription_tier_slug")
        self.region = module.params.get("region")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_registry(self):
        try:
            registry = self.client.registry.get()
            if registry:
                return registry.get("registry")
            return None
        except DigitalOceanCommonModule.HttpResponseError as err:
            if err.status_code == 404:
                return None
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                registry={},
            )

    def create_registry(self):
        try:
            body = {
                "name": self.name,
                "subscription_tier_slug": self.subscription_tier_slug,
            }
            if self.region:
                body["region"] = self.region

            registry = self.client.registry.create(body=body)["registry"]

            self.module.exit_json(
                changed=True,
                msg=f"Created container registry {self.name}",
                registry=registry,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, registry={}
            )

    def delete_registry(self):
        try:
            self.client.registry.delete()
            self.module.exit_json(
                changed=True,
                msg=f"Deleted container registry {self.name}",
                registry={},
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
                registry={},
            )

    def present(self):
        registry = self.get_registry()
        if registry is None:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Container registry {self.name} would be created",
                    registry={},
                )
            else:
                self.create_registry()
        else:
            self.module.exit_json(
                changed=False,
                msg=f"Container registry {registry.get('name')} exists",
                registry=registry,
            )

    def absent(self):
        registry = self.get_registry()
        if registry is None:
            self.module.exit_json(
                changed=False,
                msg="Container registry does not exist",
                registry={},
            )
        else:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Container registry {registry.get('name')} would be deleted",
                    registry=registry,
                )
            else:
                self.delete_registry()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        subscription_tier_slug=dict(
            type="str",
            required=False,
            choices=["starter", "basic", "professional"],
            default="basic",
        ),
        region=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    ContainerRegistry(module)


if __name__ == "__main__":
    main()
