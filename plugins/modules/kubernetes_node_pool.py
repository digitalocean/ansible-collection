#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: kubernetes_node_pool

short_description: Create, update, or delete Kubernetes node pools

version_added: 0.6.0

description:
  - Create, update, or delete node pools in a Kubernetes cluster.
  - |
    Node pools allow you to create groups of worker nodes with different
    configurations within a single Kubernetes cluster.
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
  name:
    description:
      - The name of the node pool.
    type: str
    required: true
  size:
    description:
      - The slug identifier for the size of the nodes.
    type: str
    required: false
  count:
    description:
      - The number of Droplet instances in the node pool.
    type: int
    required: false
  tags:
    description:
      - An array of tags to apply to the node pool.
    type: list
    elements: str
    required: false
  labels:
    description:
      - An object of key/value mappings specifying labels to apply to nodes.
    type: dict
    required: false
  taints:
    description:
      - An array of taints to apply to nodes in the pool.
    type: list
    elements: dict
    required: false
  auto_scale:
    description:
      - Enable auto-scaling for the node pool.
    type: bool
    required: false
    default: false
  min_nodes:
    description:
      - Minimum number of nodes for auto-scaling.
    type: int
    required: false
  max_nodes:
    description:
      - Maximum number of nodes for auto-scaling.
    type: int
    required: false
  id:
    description:
      - The unique identifier of the node pool.
      - Used for lookup when updating or deleting.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create Kubernetes node pool
  digitalocean.cloud.kubernetes_node_pool:
    token: "{{ token }}"
    state: present
    cluster_id: bd5f5959-5e1e-4205-a714-a914373942af
    name: worker-pool
    size: s-2vcpu-4gb
    count: 3
    tags:
      - production

- name: Create auto-scaling node pool
  digitalocean.cloud.kubernetes_node_pool:
    token: "{{ token }}"
    state: present
    cluster_id: bd5f5959-5e1e-4205-a714-a914373942af
    name: autoscale-pool
    size: s-2vcpu-4gb
    auto_scale: true
    min_nodes: 1
    max_nodes: 10

- name: Delete node pool
  digitalocean.cloud.kubernetes_node_pool:
    token: "{{ token }}"
    state: absent
    cluster_id: bd5f5959-5e1e-4205-a714-a914373942af
    name: worker-pool
"""


RETURN = r"""
node_pool:
  description: Node pool information.
  returned: always
  type: dict
  sample:
    id: cdda885e-7663-40c8-bc74-3a036c66545d
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
    auto_scale: false
    min_nodes: 0
    max_nodes: 0
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Node pool result information.
  returned: always
  type: str
  sample:
    - Created node pool worker-pool
    - Updated node pool worker-pool
    - Deleted node pool worker-pool
    - Node pool worker-pool would be created
    - Node pool worker-pool exists
    - Node pool worker-pool does not exist
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanConstants,
)


class KubernetesNodePool(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        self.name = module.params.get("name")
        self.size = module.params.get("size")
        self.count = module.params.get("count")
        self.tags = module.params.get("tags")
        self.labels = module.params.get("labels")
        self.taints = module.params.get("taints")
        self.auto_scale = module.params.get("auto_scale")
        self.min_nodes = module.params.get("min_nodes")
        self.max_nodes = module.params.get("max_nodes")
        self.id = module.params.get("id")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_node_pool(self):
        try:
            node_pools = self.client.kubernetes.list_node_pools(
                cluster_id=self.cluster_id
            ).get("node_pools", [])
            for pool in node_pools:
                if pool.get("name") == self.name:
                    return pool
                elif self.id and pool.get("id") == self.id:
                    return pool
            return None
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
                node_pool={},
            )

    def create_node_pool(self):
        try:
            body = {
                "name": self.name,
                "size": self.size,
                "count": self.count,
            }
            if self.tags:
                body["tags"] = self.tags
            if self.labels:
                body["labels"] = self.labels
            if self.taints:
                body["taints"] = self.taints
            if self.auto_scale:
                body["auto_scale"] = self.auto_scale
                body["min_nodes"] = self.min_nodes
                body["max_nodes"] = self.max_nodes

            node_pool = self.client.kubernetes.add_node_pool(
                cluster_id=self.cluster_id, body=body
            )["node_pool"]

            # Wait for nodes to be ready
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                current_pool = self.get_node_pool()
                if current_pool:
                    nodes = current_pool.get("nodes", [])
                    all_running = all(
                        n.get("status", {}).get("state") == "running" for n in nodes
                    )
                    if all_running and len(nodes) > 0:
                        node_pool = current_pool
                        break
                time.sleep(DigitalOceanConstants.SLEEP)

            self.module.exit_json(
                changed=True,
                msg=f"Created node pool {self.name}",
                node_pool=node_pool,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, node_pool={}
            )

    def update_node_pool(self, node_pool):
        try:
            body = {
                "name": self.name,
            }
            if self.count is not None:
                body["count"] = self.count
            if self.tags:
                body["tags"] = self.tags
            if self.labels:
                body["labels"] = self.labels
            if self.taints:
                body["taints"] = self.taints
            if self.auto_scale is not None:
                body["auto_scale"] = self.auto_scale
            if self.min_nodes is not None:
                body["min_nodes"] = self.min_nodes
            if self.max_nodes is not None:
                body["max_nodes"] = self.max_nodes

            updated_pool = self.client.kubernetes.update_node_pool(
                cluster_id=self.cluster_id, node_pool_id=node_pool["id"], body=body
            )["node_pool"]

            self.module.exit_json(
                changed=True,
                msg=f"Updated node pool {self.name}",
                node_pool=updated_pool,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, node_pool={}
            )

    def delete_node_pool(self, node_pool):
        try:
            self.client.kubernetes.delete_node_pool(
                cluster_id=self.cluster_id, node_pool_id=node_pool["id"]
            )
            self.module.exit_json(
                changed=True,
                msg=f"Deleted node pool {self.name}",
                node_pool={},
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
                node_pool={},
            )

    def present(self):
        node_pool = self.get_node_pool()
        if node_pool is None:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Node pool {self.name} would be created",
                    node_pool={},
                )
            else:
                if not self.size or self.count is None:
                    self.module.fail_json(
                        changed=False,
                        msg="size and count are required when creating a node pool",
                        node_pool={},
                    )
                self.create_node_pool()
        else:
            # Check if update is needed
            needs_update = False
            if self.count is not None and self.count != node_pool.get("count"):
                needs_update = True
            if self.auto_scale is not None and self.auto_scale != node_pool.get(
                "auto_scale"
            ):
                needs_update = True

            if needs_update:
                if self.module.check_mode:
                    self.module.exit_json(
                        changed=True,
                        msg=f"Node pool {self.name} would be updated",
                        node_pool=node_pool,
                    )
                else:
                    self.update_node_pool(node_pool)
            else:
                self.module.exit_json(
                    changed=False,
                    msg=f"Node pool {self.name} exists",
                    node_pool=node_pool,
                )

    def absent(self):
        node_pool = self.get_node_pool()
        if node_pool is None:
            self.module.exit_json(
                changed=False,
                msg=f"Node pool {self.name} does not exist",
                node_pool={},
            )
        else:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Node pool {self.name} would be deleted",
                    node_pool=node_pool,
                )
            else:
                self.delete_node_pool(node_pool)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
        name=dict(type="str", required=True),
        size=dict(type="str", required=False),
        count=dict(type="int", required=False),
        tags=dict(type="list", elements="str", required=False),
        labels=dict(type="dict", required=False),
        taints=dict(type="list", elements="dict", required=False),
        auto_scale=dict(type="bool", required=False, default=False),
        min_nodes=dict(type="int", required=False),
        max_nodes=dict(type="int", required=False),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    KubernetesNodePool(module)


if __name__ == "__main__":
    main()
