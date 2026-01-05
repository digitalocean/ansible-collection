#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_user

short_description: Create or delete database users

version_added: 1.9.0

description:
  - Create or delete database users in a managed database cluster.
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
      - The name of the database user.
    type: str
    required: true
  mysql_settings:
    description:
      - MySQL-specific settings for the user.
    type: dict
    required: false
    suboptions:
      auth_plugin:
        description:
          - The authentication plugin for the user.
        type: str
        choices:
          - mysql_native_password
          - caching_sha2_password
  readonly:
    description:
      - For PostgreSQL and MySQL clusters, set to true to create a read-only user.
    type: bool
    required: false
    default: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create database user
  digitalocean.cloud.database_user:
    token: "{{ token }}"
    state: present
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    name: app_user

- name: Create read-only database user
  digitalocean.cloud.database_user:
    token: "{{ token }}"
    state: present
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    name: readonly_user
    readonly: true

- name: Delete database user
  digitalocean.cloud.database_user:
    token: "{{ token }}"
    state: absent
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    name: app_user
"""


RETURN = r"""
user:
  description: Database user information.
  returned: always
  type: dict
  sample:
    name: app_user
    role: normal
    password: wv78n3zpz42xezdk
    mysql_settings:
      auth_plugin: caching_sha2_password
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Database user result information.
  returned: always
  type: str
  sample:
    - Created database user app_user
    - Deleted database user app_user
    - Database user app_user would be created
    - Database user app_user exists
    - Database user app_user does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DatabaseUser(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        self.name = module.params.get("name")
        self.mysql_settings = module.params.get("mysql_settings")
        self.readonly = module.params.get("readonly")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_user(self):
        try:
            users = self.client.databases.list_users(
                database_cluster_uuid=self.cluster_id
            ).get("users", [])
            for user in users:
                if user.get("name") == self.name:
                    return user
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
                user={},
            )

    def create_user(self):
        try:
            body = {
                "name": self.name,
            }
            if self.mysql_settings:
                body["mysql_settings"] = self.mysql_settings
            if self.readonly:
                body["readonly"] = self.readonly

            user = self.client.databases.add_user(
                database_cluster_uuid=self.cluster_id, body=body
            )["user"]

            self.module.exit_json(
                changed=True,
                msg=f"Created database user {self.name}",
                user=user,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, user={}
            )

    def delete_user(self):
        try:
            self.client.databases.delete_user(
                database_cluster_uuid=self.cluster_id, username=self.name
            )
            self.module.exit_json(
                changed=True,
                msg=f"Deleted database user {self.name}",
                user={},
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
                user={},
            )

    def present(self):
        user = self.get_user()
        if user is None:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Database user {self.name} would be created",
                    user={},
                )
            else:
                self.create_user()
        else:
            self.module.exit_json(
                changed=False,
                msg=f"Database user {self.name} exists",
                user=user,
            )

    def absent(self):
        user = self.get_user()
        if user is None:
            self.module.exit_json(
                changed=False,
                msg=f"Database user {self.name} does not exist",
                user={},
            )
        else:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Database user {self.name} would be deleted",
                    user=user,
                )
            else:
                self.delete_user()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
        name=dict(type="str", required=True),
        mysql_settings=dict(type="dict", required=False),
        readonly=dict(type="bool", required=False, default=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    DatabaseUser(module)


if __name__ == "__main__":
    main()
