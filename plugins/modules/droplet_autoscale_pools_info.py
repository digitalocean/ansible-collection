#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: droplet_autoscale_pools_info

short_description: List all Droplet Autoscale Pools on your account

version_added: 1.9.0

description:
  - List all Droplet Autoscale Pools on your account.
  - |
    Droplet Autoscale Pools allow you to automatically scale the number of
    Droplets in a pool based on resource utilization or scheduled times.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Droplet-Autoscale-Pools).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get Droplet Autoscale Pools
  digitalocean.cloud.droplet_autoscale_pools_info:
    token: "{{ token }}"
"""


RETURN = r"""
droplet_autoscale_pools:
  description: Droplet Autoscale Pools.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
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
  description: Droplet Autoscale Pools result information.
  returned: always
  type: str
  sample:
    - Current Droplet Autoscale Pools
    - No Droplet Autoscale Pools
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class DropletAutoscalePoolsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        autoscale_pools = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.droplets,
            meth="list_autoscale_pools",
            key="autoscale_pools",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if autoscale_pools:
            self.module.exit_json(
                changed=False,
                msg="Current Droplet Autoscale Pools",
                droplet_autoscale_pools=autoscale_pools,
            )
        self.module.exit_json(
            changed=False,
            msg="No Droplet Autoscale Pools",
            droplet_autoscale_pools=[],
        )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    DropletAutoscalePoolsInformation(module)


if __name__ == "__main__":
    main()
