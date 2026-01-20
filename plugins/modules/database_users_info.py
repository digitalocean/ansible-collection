#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_users_info

short_description: List all database users in a cluster

version_added: 1.9.0

description:
  - List all database users in a managed database cluster.
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
- name: Get database users
  digitalocean.cloud.database_users_info:
    token: "{{ token }}"
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
"""


RETURN = r"""
users:
  description: Database users.
  returned: always
  type: list
  elements: dict
  sample:
    - name: doadmin
      role: primary
      password: example-password
    - name: app_user
      role: normal
      password: abc123xyz789
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Database users result information.
  returned: always
  type: str
  sample:
    - Current database users
    - No database users
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DatabaseUsersInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            users = self.client.databases.list_users(
                database_cluster_uuid=self.cluster_id
            ).get("users", [])
            if users:
                self.module.exit_json(
                    changed=False,
                    msg="Current database users",
                    users=users,
                )
            self.module.exit_json(changed=False, msg="No database users", users=[])
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
                users=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    DatabaseUsersInformation(module)


if __name__ == "__main__":
    main()
