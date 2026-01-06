#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: function_namespace

short_description: Create or delete Functions namespaces

version_added: 1.9.0

description:
  - Create or delete Functions namespaces.
  - |
    DigitalOcean Functions is a serverless computing solution that runs
    on-demand, allowing you to focus on code without managing infrastructure.
    Namespaces are containers for functions.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Functions).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  namespace:
    description:
      - The name of the namespace.
    type: str
    required: true
  region:
    description:
      - The slug identifier for the region where the namespace will be created.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create Functions namespace
  digitalocean.cloud.function_namespace:
    token: "{{ token }}"
    state: present
    namespace: my-namespace
    region: nyc1

- name: Delete Functions namespace
  digitalocean.cloud.function_namespace:
    token: "{{ token }}"
    state: absent
    namespace: my-namespace
"""


RETURN = r"""
namespace:
  description: Functions namespace information.
  returned: always
  type: dict
  sample:
    namespace: my-namespace
    region: nyc1
    uuid: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    created_at: '2020-03-13T19:20:47.442049222Z'
    updated_at: '2020-03-13T19:20:47.442049222Z'
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Functions namespace result information.
  returned: always
  type: str
  sample:
    - Created namespace my-namespace
    - Deleted namespace my-namespace
    - Namespace my-namespace would be created
    - Namespace my-namespace exists
    - Namespace my-namespace does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class FunctionNamespace(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.namespace = module.params.get("namespace")
        self.region = module.params.get("region")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_namespaces(self):
        try:
            # Functions API doesn't support pagination parameters
            response = self.client.functions.list_namespaces()
            if response is None:
                return []
            namespaces = response.get("namespaces", [])
            if namespaces is None:
                return []
            found_namespaces = []
            for ns in namespaces:
                if self.namespace == ns.get("namespace"):
                    found_namespaces.append(ns)
            return found_namespaces
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
                namespace={},
            )

    def create_namespace(self):
        try:
            body = {
                "label": self.namespace,
                "region": self.region,
            }
            namespace = self.client.functions.create_namespace(body=body)["namespace"]

            self.module.exit_json(
                changed=True,
                msg=f"Created namespace {self.namespace}",
                namespace=namespace,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, namespace={}
            )

    def delete_namespace(self, namespace):
        try:
            self.client.functions.delete_namespace(namespace_id=namespace["uuid"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted namespace {self.namespace}",
                namespace=namespace,
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
                namespace={},
            )

    def present(self):
        namespaces = self.get_namespaces()
        if len(namespaces) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Namespace {self.namespace} would be created",
                    namespace={},
                )
            else:
                if not self.region:
                    self.module.fail_json(
                        changed=False,
                        msg="region is required when creating a namespace",
                        namespace={},
                    )
                self.create_namespace()
        elif len(namespaces) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Namespace {self.namespace} exists",
                namespace=namespaces[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(namespaces)} namespaces named {self.namespace}",
                namespace={},
            )

    def absent(self):
        namespaces = self.get_namespaces()
        if len(namespaces) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Namespace {self.namespace} does not exist",
                namespace={},
            )
        elif len(namespaces) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Namespace {self.namespace} would be deleted",
                    namespace=namespaces[0],
                )
            else:
                self.delete_namespace(namespace=namespaces[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(namespaces)} namespaces named {self.namespace}",
                namespace={},
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        namespace=dict(type="str", required=True),
        region=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    FunctionNamespace(module)


if __name__ == "__main__":
    main()
