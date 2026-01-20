#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_replicas_info

short_description: List all read-only replicas for a database cluster

version_added: 1.9.0

description:
  - List all read-only replicas for a database cluster.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Databases).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  cluster_id:
    description:
      - The UUID of the database cluster.
    type: str
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get database replicas
  digitalocean.cloud.database_replicas_info:
    token: "{{ token }}"
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
"""


RETURN = r"""
replicas:
  description: Database replicas.
  returned: always
  type: list
  elements: dict
  sample:
    - name: read-replica-nyc1
      region: nyc1
      status: online
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
  description: Database replicas result information.
  returned: always
  type: str
  sample:
    - Current database replicas
    - No database replicas
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DatabaseReplicasInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            response = self.client.databases.list_replicas(
                database_cluster_uuid=self.cluster_id
            )
            replicas = response.get("replicas", []) if response else []
            if replicas:
                self.module.exit_json(
                    changed=False,
                    msg="Current database replicas",
                    replicas=replicas,
                )
            self.module.exit_json(
                changed=False, msg="No database replicas", replicas=[]
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
                replicas=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    DatabaseReplicasInformation(module)


if __name__ == "__main__":
    main()
