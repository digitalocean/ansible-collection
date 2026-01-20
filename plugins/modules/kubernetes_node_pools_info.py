#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: kubernetes_node_pools_info

short_description: List all node pools in a Kubernetes cluster

version_added: 1.9.0

description:
  - List all node pools in a Kubernetes cluster.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Kubernetes).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  cluster_id:
    description:
      - The UUID of the Kubernetes cluster.
    type: str
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get Kubernetes node pools
  digitalocean.cloud.kubernetes_node_pools_info:
    token: "{{ token }}"
    cluster_id: bd5f5959-5e1e-4205-a714-a914373942af
"""


RETURN = r"""
node_pools:
  description: Node pools.
  returned: always
  type: list
  elements: dict
  sample:
    - id: cdda885e-7663-40c8-bc74-3a036c66545d
      name: worker-pool
      size: s-2vcpu-4gb
      count: 3
      tags:
        - production
      nodes:
        - id: 123abc
          name: worker-pool-abc123
          status:
            state: running
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Node pools result information.
  returned: always
  type: str
  sample:
    - Current node pools
    - No node pools
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class KubernetesNodePoolsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            node_pools = self.client.kubernetes.list_node_pools(
                cluster_id=self.cluster_id
            ).get("node_pools", [])
            if node_pools:
                self.module.exit_json(
                    changed=False,
                    msg="Current node pools",
                    node_pools=node_pools,
                )
            self.module.exit_json(changed=False, msg="No node pools", node_pools=[])
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
                node_pools=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    KubernetesNodePoolsInformation(module)


if __name__ == "__main__":
    main()
