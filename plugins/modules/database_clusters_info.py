#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_clusters_info

short_description: List all of the database clusters on your account

version_added: 0.2.0

description:
  - List all of the database clusters on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/databases_list_clusters).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  tag_name:
    description: Limits the results to database clusters with a specific tag.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get database clusters
  digitalocean.cloud.database_clusters_info:
    token: "{{ token }}"
"""


RETURN = r"""
databases:
  description: Database clusters.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
      name: backend
      engine: pg
      version: 10
      connection:
        uri: 'postgres://doadmin:wv78n3zpz42xezdk@backend-do-user-19081923-0.db.ondigitalocean.com:25060/defaultdb?sslmode=require'
        database: ""
        host: backend-do-user-19081923-0.db.ondigitalocean.com
        port: 25060,
        user: doadmin
        password: wv78n3zpz42xezdk
        ssl: true
      private_connection:
        uri: 'postgres://doadmin:wv78n3zpz42xezdk@private-backend-do-user-19081923-0.db.ondigitalocean.com:25060/defaultdb?sslmode=require'
        database: ""
        host: private-backend-do-user-19081923-0.db.ondigitalocean.com
        port: 25060
        user: doadmin
        password: wv78n3zpz42xezdk
        ssl: true
      users:
        - name: doadmin
          role: primary
          password: wv78n3zpz42xezdk
      db_names:
        - defaultdb
      num_nodes: 1
      region: nyc3
      status: online
      created_at: '2019-01-11T18:37:36Z'
      maintenance_window:
        day: saturday
        hour: '08:45:12'
        pending: true
        description:
          - Update TimescaleDB to version 1.2.1
          - Upgrade to PostgreSQL 11.2 and 10.7 bugfix releases
      size: db-s-2vcpu-4gb
      tags:
        - production
      private_network_uuid: d455e75d-4858-4eec-8c95-da2f0a5f93a7
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Database clusters information.
  returned: always
  type: str
  sample:
    - Current database clusters
    - No database clusters
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DatabaseClustersInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.tag_name = module.params.get("tag_name")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            if self.tag_name:
                database_clusters = self.client.databases.list_clusters(
                    tag_name=self.tag_name
                )
            else:
                database_clusters = self.client.databases.list_clusters()
            databases = database_clusters.get("databases")
            if databases:
                self.module.exit_json(
                    changed=False, msg="Current database clusters", databases=databases
                )
            self.module.exit_json(
                changed=False, msg="No database clusters", databases=[]
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(changed=False, msg=error.get("Message"), error=error)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(tag_name=dict(type="str", required=False))
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    DatabaseClustersInformation(module)


if __name__ == "__main__":
    main()
