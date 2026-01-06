#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_db

short_description: Create or delete databases within a cluster

version_added: 1.9.0

description:
  - Create or delete databases within a managed database cluster.
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
      - The name of the database.
    type: str
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create database
  digitalocean.cloud.database_db:
    token: "{{ token }}"
    state: present
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    name: my_database

- name: Delete database
  digitalocean.cloud.database_db:
    token: "{{ token }}"
    state: absent
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    name: my_database
"""


RETURN = r"""
db:
  description: Database information.
  returned: always
  type: dict
  sample:
    name: my_database
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Database result information.
  returned: always
  type: str
  sample:
    - Created database my_database
    - Deleted database my_database
    - Database my_database would be created
    - Database my_database exists
    - Database my_database does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DatabaseDB(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        self.name = module.params.get("name")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_db(self):
        try:
            dbs = self.client.databases.list(database_cluster_uuid=self.cluster_id).get(
                "dbs", []
            )
            for db in dbs:
                if db.get("name") == self.name:
                    return db
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
                db={},
            )

    def create_db(self):
        try:
            body = {
                "name": self.name,
            }
            db = self.client.databases.add(
                database_cluster_uuid=self.cluster_id, body=body
            )["db"]

            self.module.exit_json(
                changed=True,
                msg=f"Created database {self.name}",
                db=db,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, db={}
            )

    def delete_db(self):
        try:
            self.client.databases.delete(
                database_cluster_uuid=self.cluster_id, database_name=self.name
            )
            self.module.exit_json(
                changed=True,
                msg=f"Deleted database {self.name}",
                db={},
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
                db={},
            )

    def present(self):
        db = self.get_db()
        if db is None:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Database {self.name} would be created",
                    db={},
                )
            else:
                self.create_db()
        else:
            self.module.exit_json(
                changed=False,
                msg=f"Database {self.name} exists",
                db=db,
            )

    def absent(self):
        db = self.get_db()
        if db is None:
            self.module.exit_json(
                changed=False,
                msg=f"Database {self.name} does not exist",
                db={},
            )
        else:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Database {self.name} would be deleted",
                    db=db,
                )
            else:
                self.delete_db()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
        name=dict(type="str", required=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    DatabaseDB(module)


if __name__ == "__main__":
    main()
