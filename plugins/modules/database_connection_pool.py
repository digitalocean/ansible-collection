#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_connection_pool

short_description: Create or delete database connection pools

version_added: 0.6.0

description:
  - Create or delete connection pools for PostgreSQL database clusters.
  - Connection pools can be used to allow a database to share its idle connections.
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
      - The name of the connection pool.
    type: str
    required: true
  mode:
    description:
      - The PgBouncer transaction mode for the connection pool.
    type: str
    required: false
    choices:
      - session
      - transaction
      - statement
    default: transaction
  size:
    description:
      - The desired size of the PgBouncer connection pool.
    type: int
    required: false
    default: 10
  db:
    description:
      - The database for use with the connection pool.
    type: str
    required: true
  user:
    description:
      - The name of the user for use with the connection pool.
    type: str
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create connection pool
  digitalocean.cloud.database_connection_pool:
    token: "{{ token }}"
    state: present
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    name: my_pool
    mode: transaction
    size: 10
    db: defaultdb
    user: doadmin

- name: Delete connection pool
  digitalocean.cloud.database_connection_pool:
    token: "{{ token }}"
    state: absent
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    name: my_pool
    db: defaultdb
    user: doadmin
"""


RETURN = r"""
pool:
  description: Connection pool information.
  returned: always
  type: dict
  sample:
    name: my_pool
    mode: transaction
    size: 10
    db: defaultdb
    user: doadmin
    connection:
      uri: postgres://doadmin:wv78n3zpz42xezdk@...
      database: my_pool
      host: host.db.ondigitalocean.com
      port: 25061
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
  description: Connection pool result information.
  returned: always
  type: str
  sample:
    - Created connection pool my_pool
    - Deleted connection pool my_pool
    - Connection pool my_pool would be created
    - Connection pool my_pool exists
    - Connection pool my_pool does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DatabaseConnectionPool(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        self.name = module.params.get("name")
        self.mode = module.params.get("mode")
        self.size = module.params.get("size")
        self.db = module.params.get("db")
        self.user = module.params.get("user")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_pool(self):
        try:
            pools = self.client.databases.list_connection_pools(
                database_cluster_uuid=self.cluster_id
            ).get("pools", [])
            for pool in pools:
                if pool.get("name") == self.name:
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
                pool={},
            )

    def create_pool(self):
        try:
            body = {
                "name": self.name,
                "mode": self.mode,
                "size": self.size,
                "db": self.db,
                "user": self.user,
            }
            pool = self.client.databases.add_connection_pool(
                database_cluster_uuid=self.cluster_id, body=body
            )["pool"]

            self.module.exit_json(
                changed=True,
                msg=f"Created connection pool {self.name}",
                pool=pool,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, pool={}
            )

    def delete_pool(self):
        try:
            self.client.databases.delete_connection_pool(
                database_cluster_uuid=self.cluster_id, pool_name=self.name
            )
            self.module.exit_json(
                changed=True,
                msg=f"Deleted connection pool {self.name}",
                pool={},
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
                pool={},
            )

    def present(self):
        pool = self.get_pool()
        if pool is None:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Connection pool {self.name} would be created",
                    pool={},
                )
            else:
                self.create_pool()
        else:
            self.module.exit_json(
                changed=False,
                msg=f"Connection pool {self.name} exists",
                pool=pool,
            )

    def absent(self):
        pool = self.get_pool()
        if pool is None:
            self.module.exit_json(
                changed=False,
                msg=f"Connection pool {self.name} does not exist",
                pool={},
            )
        else:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Connection pool {self.name} would be deleted",
                    pool=pool,
                )
            else:
                self.delete_pool()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
        name=dict(type="str", required=True),
        mode=dict(
            type="str",
            required=False,
            choices=["session", "transaction", "statement"],
            default="transaction",
        ),
        size=dict(type="int", required=False, default=10),
        db=dict(type="str", required=True),
        user=dict(type="str", required=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    DatabaseConnectionPool(module)


if __name__ == "__main__":
    main()
