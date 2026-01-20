#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplet_autoscale_pool

short_description: Create or delete Droplet Autoscale Pools

version_added: 1.9.0

description:
  - Create or delete Droplet Autoscale Pools.
  - |
    Droplet Autoscale Pools allow you to automatically scale the number of
    Droplets in a pool based on resource utilization or scheduled times.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Droplet-Autoscale-Pools).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The name of the Droplet Autoscale Pool.
    type: str
    required: true
  config:
    description:
      - Configuration for the autoscale pool.
    type: dict
    required: false
    suboptions:
      min_instances:
        description:
          - Minimum number of Droplets in the pool.
        type: int
      max_instances:
        description:
          - Maximum number of Droplets in the pool.
        type: int
      target_cpu_utilization:
        description:
          - Target CPU utilization percentage for scaling.
        type: float
      target_memory_utilization:
        description:
          - Target memory utilization percentage for scaling.
        type: float
      cooldown_minutes:
        description:
          - Cooldown period in minutes between scaling actions.
        type: int
  droplet_template:
    description:
      - Template for creating Droplets in the pool.
    type: dict
    required: false
    suboptions:
      size:
        description:
          - The slug identifier for the size of the Droplets.
        type: str
      region:
        description:
          - The slug identifier for the region.
        type: str
      image:
        description:
          - The image ID or slug for the Droplet.
        type: str
      ssh_keys:
        description:
          - An array of SSH key IDs or fingerprints.
        type: list
        elements: str
      vpc_uuid:
        description:
          - The UUID of the VPC.
        type: str
      tags:
        description:
          - A list of tags to apply to the Droplets.
        type: list
        elements: str
      user_data:
        description:
          - User data to provide to the Droplets.
        type: str
  id:
    description:
      - The unique identifier of the Droplet Autoscale Pool.
      - Used for lookup when deleting or updating.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create Droplet Autoscale Pool
  digitalocean.cloud.droplet_autoscale_pool:
    token: "{{ token }}"
    state: present
    name: my-autoscale-pool
    config:
      min_instances: 1
      max_instances: 10
      target_cpu_utilization: 0.7
      cooldown_minutes: 5
    droplet_template:
      size: s-1vcpu-1gb
      region: nyc1
      image: ubuntu-22-04-x64
      ssh_keys:
        - "{{ ssh_key_id }}"

- name: Delete Droplet Autoscale Pool
  digitalocean.cloud.droplet_autoscale_pool:
    token: "{{ token }}"
    state: absent
    name: my-autoscale-pool
"""


RETURN = r"""
droplet_autoscale_pool:
  description: Droplet Autoscale Pool information.
  returned: always
  type: dict
  sample:
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    name: my-autoscale-pool
    config:
      min_instances: 1
      max_instances: 10
      target_cpu_utilization: 0.7
      cooldown_minutes: 5
    droplet_template:
      size: s-1vcpu-1gb
      region: nyc1
      image: ubuntu-22-04-x64
    status: active
    created_at: '2020-03-13T19:20:47.442049222Z'
    current_utilization:
      cpu: 0.45
      memory: 0.32
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Droplet Autoscale Pool result information.
  returned: always
  type: str
  sample:
    - Created Droplet Autoscale Pool my-autoscale-pool
    - Deleted Droplet Autoscale Pool my-autoscale-pool
    - Droplet Autoscale Pool my-autoscale-pool would be created
    - Droplet Autoscale Pool my-autoscale-pool exists
    - Droplet Autoscale Pool my-autoscale-pool does not exist
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
    DigitalOceanConstants,
)


class DropletAutoscalePool(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.config = module.params.get("config")
        self.droplet_template = module.params.get("droplet_template")
        self.id = module.params.get("id")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_autoscale_pools(self):
        try:
            autoscale_pools = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.autoscalepools,
                meth="list",
                key="autoscale_pools",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            found_pools = []
            for pool in autoscale_pools:
                if self.name == pool.get("name"):
                    found_pools.append(pool)
                elif self.id and self.id == pool.get("id"):
                    found_pools.append(pool)
            return found_pools
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
                droplet_autoscale_pool=[],
            )

    def create_autoscale_pool(self):
        try:
            body = {
                "name": self.name,
            }
            if self.config:
                body["config"] = self.config
            if self.droplet_template:
                body["droplet_template"] = self.droplet_template

            pool = self.client.autoscalepools.create(body=body)["autoscale_pool"]

            # Wait for the pool to become active
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                status = pool.get("status", "").lower()
                if status == "active":
                    break
                time.sleep(DigitalOceanConstants.SLEEP)
                try:
                    pool = self.client.autoscalepools.get(autoscale_pool_id=pool["id"])[
                        "autoscale_pool"
                    ]
                except DigitalOceanCommonModule.HttpResponseError:
                    pass

            self.module.exit_json(
                changed=True,
                msg=f"Created Droplet Autoscale Pool {self.name} ({pool['id']})",
                droplet_autoscale_pool=pool,
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
                droplet_autoscale_pool=[],
            )

    def delete_autoscale_pool(self, pool):
        try:
            pool_id = pool["id"]
            self.client.autoscalepools.delete(autoscale_pool_id=pool_id)

            # Wait a short period to allow the deletion to propagate
            # Deleting an autoscale pool with active Droplets triggers asynchronous cleanup
            # of child resources, which can take considerable time (5-10+ minutes).
            # We sleep briefly to allow the deletion to register, then return.
            time.sleep(DigitalOceanConstants.SLEEP * 2)

            self.module.exit_json(
                changed=True,
                msg=f"Deleted Droplet Autoscale Pool {self.name} ({pool_id})",
                droplet_autoscale_pool=pool,
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
                droplet_autoscale_pool=[],
            )

    def present(self):
        pools = self.get_autoscale_pools()
        if len(pools) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Droplet Autoscale Pool {self.name} would be created",
                    droplet_autoscale_pool=[],
                )
            else:
                self.create_autoscale_pool()
        elif len(pools) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Droplet Autoscale Pool {self.name} ({pools[0]['id']}) exists",
                droplet_autoscale_pool=pools[0],
            )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(pools)} Droplet Autoscale Pools named {self.name}",
                droplet_autoscale_pool=[],
            )

    def absent(self):
        pools = self.get_autoscale_pools()
        if len(pools) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"Droplet Autoscale Pool {self.name} does not exist",
                droplet_autoscale_pool=[],
            )
        elif len(pools) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Droplet Autoscale Pool {self.name} ({pools[0]['id']}) would be deleted",
                    droplet_autoscale_pool=pools[0],
                )
            else:
                self.delete_autoscale_pool(pool=pools[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(pools)} Droplet Autoscale Pools named {self.name}",
                droplet_autoscale_pool=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        config=dict(
            type="dict",
            required=False,
            options=dict(
                min_instances=dict(type="int", required=False),
                max_instances=dict(type="int", required=False),
                target_cpu_utilization=dict(type="float", required=False),
                target_memory_utilization=dict(type="float", required=False),
                cooldown_minutes=dict(type="int", required=False),
            ),
        ),
        droplet_template=dict(
            type="dict",
            required=False,
            options=dict(
                size=dict(type="str", required=False),
                region=dict(type="str", required=False),
                image=dict(type="str", required=False),
                ssh_keys=dict(type="list", elements="str", required=False, no_log=True),
                vpc_uuid=dict(type="str", required=False),
                tags=dict(type="list", elements="str", required=False),
                user_data=dict(type="str", required=False),
            ),
        ),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    DropletAutoscalePool(module)


if __name__ == "__main__":
    main()
