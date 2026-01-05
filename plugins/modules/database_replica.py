#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_replica

short_description: Create or delete database read-only replicas

version_added: 1.9.0

description:
  - Create or delete read-only replicas for a database cluster.
  - |
    Read-only replicas allow you to increase read throughput by offloading
    read queries to replica nodes.
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
  name:
    description:
      - The name of the read-only replica.
    type: str
    required: true
  region:
    description:
      - The slug identifier for the region where the replica will be created.
    type: str
    required: false
  size:
    description:
      - The slug identifier for the size of the replica node.
    type: str
    required: false
  tags:
    description:
      - An array of tags to apply to the replica.
    type: list
    elements: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create database replica
  digitalocean.cloud.database_replica:
    token: "{{ token }}"
    state: present
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    name: read-replica-nyc1
    region: nyc1
    size: db-s-1vcpu-1gb

- name: Delete database replica
  digitalocean.cloud.database_replica:
    token: "{{ token }}"
    state: absent
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    name: read-replica-nyc1
"""


RETURN = r"""
replica:
  description: Database replica information.
  returned: always
  type: dict
  sample:
    name: read-replica-nyc1
    region: nyc1
    status: online
    created_at: '2020-03-13T19:20:47.442049222Z'
    connection:
      uri: postgres://doadmin:wv78n3zpz42xezdk@...
      host: read-replica-nyc1.db.ondigitalocean.com
      port: 25060
      user: doadmin
      password: wv78n3zpz42xezdk
      ssl: true
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Database replica result information.
  returned: always
  type: str
  sample:
    - Created database replica read-replica-nyc1
    - Deleted database replica read-replica-nyc1
    - Database replica read-replica-nyc1 would be created
    - Database replica read-replica-nyc1 exists
    - Database replica read-replica-nyc1 does not exist
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanConstants,
)


class DatabaseReplica(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        self.name = module.params.get("name")
        self.region = module.params.get("region")
        self.size = module.params.get("size")
        self.tags = module.params.get("tags")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_replica(self):
        try:
            replicas = self.client.databases.list_replicas(
                database_cluster_uuid=self.cluster_id
            ).get("replicas", [])
            for replica in replicas:
                if replica.get("name") == self.name:
                    return replica
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
                replica={},
            )

    def create_replica(self):
        try:
            body = {
                "name": self.name,
            }
            if self.region:
                body["region"] = self.region
            if self.size:
                body["size"] = self.size
            if self.tags:
                body["tags"] = self.tags

            replica = self.client.databases.create_replica(
                database_cluster_uuid=self.cluster_id, body=body
            )["replica"]

            # Wait for replica to come online
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                status = replica.get("status", "").lower()
                if status == "online":
                    break
                time.sleep(DigitalOceanConstants.SLEEP)
                replica = self.get_replica() or replica

            self.module.exit_json(
                changed=True,
                msg=f"Created database replica {self.name}",
                replica=replica,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, replica={}
            )

    def delete_replica(self):
        try:
            self.client.databases.destroy_replica(
                database_cluster_uuid=self.cluster_id, replica_name=self.name
            )
            self.module.exit_json(
                changed=True,
                msg=f"Deleted database replica {self.name}",
                replica={},
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
                replica={},
            )

    def present(self):
        replica = self.get_replica()
        if replica is None:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Database replica {self.name} would be created",
                    replica={},
                )
            else:
                self.create_replica()
        else:
            self.module.exit_json(
                changed=False,
                msg=f"Database replica {self.name} exists",
                replica=replica,
            )

    def absent(self):
        replica = self.get_replica()
        if replica is None:
            self.module.exit_json(
                changed=False,
                msg=f"Database replica {self.name} does not exist",
                replica={},
            )
        else:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Database replica {self.name} would be deleted",
                    replica=replica,
                )
            else:
                self.delete_replica()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
        name=dict(type="str", required=True),
        region=dict(type="str", required=False),
        size=dict(type="str", required=False),
        tags=dict(type="list", elements="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    DatabaseReplica(module)


if __name__ == "__main__":
    main()
