#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_config

short_description: Configure database cluster settings

version_added: 1.9.0

description:
  - Configure engine-specific settings for a database cluster.
  - |
    Different database engines support different configuration options.
    This module allows you to set options like eviction policies for
    Redis/Valkey, SQL mode for MySQL, and other engine-specific settings.
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
  config:
    description:
      - The configuration settings for the database cluster.
      - Settings vary by database engine.
    type: dict
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Configure Valkey eviction policy
  digitalocean.cloud.database_config:
    token: "{{ token }}"
    state: present
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    config:
      redis_maxmemory_policy: allkeys-lru

- name: Configure MySQL settings
  digitalocean.cloud.database_config:
    token: "{{ token }}"
    state: present
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    config:
      sql_mode: TRADITIONAL
      connect_timeout: 30

- name: Configure PostgreSQL settings
  digitalocean.cloud.database_config:
    token: "{{ token }}"
    state: present
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    config:
      autovacuum_vacuum_cost_delay: 20
      log_min_duration_statement: 1000
"""


RETURN = r"""
config:
  description: Database configuration settings.
  returned: always
  type: dict
  sample:
    redis_maxmemory_policy: allkeys-lru
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Database config result information.
  returned: always
  type: str
  sample:
    - Updated database configuration
    - Database configuration would be updated
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DatabaseConfig(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        self.config = module.params.get("config")

        if self.state == "present":
            self.present()

    def get_config(self):
        try:
            result = self.client.databases.get_config(
                database_cluster_uuid=self.cluster_id
            )
            return result.get("config", {})
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
                config={},
            )

    def update_config(self):
        try:
            body = {
                "config": self.config,
            }
            self.client.databases.patch_config(
                database_cluster_uuid=self.cluster_id, body=body
            )

            # Get the updated config
            config = self.get_config()

            self.module.exit_json(
                changed=True,
                msg="Updated database configuration",
                config=config,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, config={}
            )

    def present(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg="Database configuration would be updated",
                config={},
            )
        else:
            self.update_config()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
        config=dict(type="dict", required=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    DatabaseConfig(module)


if __name__ == "__main__":
    main()
