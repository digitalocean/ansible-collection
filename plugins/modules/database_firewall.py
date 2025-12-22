#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_firewall

short_description: Manage database cluster firewall rules

version_added: 0.6.0

description:
  - Configure firewall rules for a database cluster.
  - |
    Database firewall rules restrict which resources can connect to your
    database cluster. By default, database clusters are accessible from
    any source.
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
  rules:
    description:
      - An array of firewall rules for the database cluster.
      - Setting this replaces all existing rules.
    type: list
    elements: dict
    required: true
    suboptions:
      type:
        description:
          - The type of resource that the firewall rule allows to access the database cluster.
        type: str
        required: true
        choices:
          - droplet
          - k8s
          - ip_addr
          - tag
          - app
      value:
        description:
          - The ID of the resource, name of tag, CIDR IP address, or app name.
        type: str
        required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Configure database firewall rules
  digitalocean.cloud.database_firewall:
    token: "{{ token }}"
    state: present
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    rules:
      - type: ip_addr
        value: 192.168.1.0/24
      - type: droplet
        value: "12345678"
      - type: k8s
        value: bd5f5959-5e1e-4205-a714-a914373942af
      - type: tag
        value: backend

- name: Remove all firewall rules (allow all)
  digitalocean.cloud.database_firewall:
    token: "{{ token }}"
    state: present
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    rules: []
"""


RETURN = r"""
rules:
  description: Database firewall rules.
  returned: always
  type: list
  elements: dict
  sample:
    - uuid: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      cluster_uuid: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
      type: ip_addr
      value: 192.168.1.0/24
      created_at: '2020-03-13T19:20:47Z'
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Database firewall result information.
  returned: always
  type: str
  sample:
    - Updated database firewall rules
    - Database firewall rules would be updated
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DatabaseFirewall(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        self.rules = module.params.get("rules")

        if self.state == "present":
            self.present()

    def get_firewall_rules(self):
        try:
            result = self.client.databases.list_firewall_rules(
                database_cluster_uuid=self.cluster_id
            )
            return result.get("rules", [])
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
                rules=[],
            )

    def update_firewall_rules(self):
        try:
            body = {
                "rules": self.rules,
            }
            self.client.databases.update_firewall_rules(
                database_cluster_uuid=self.cluster_id, body=body
            )

            # Get the updated rules
            rules = self.get_firewall_rules()

            self.module.exit_json(
                changed=True,
                msg="Updated database firewall rules",
                rules=rules,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, rules=[]
            )

    def present(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg="Database firewall rules would be updated",
                rules=[],
            )
        else:
            self.update_firewall_rules()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
        rules=dict(type="list", elements="dict", required=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    DatabaseFirewall(module)


if __name__ == "__main__":
    main()
