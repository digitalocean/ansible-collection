#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_firewall_rules_info

short_description: List database cluster firewall rules

version_added: 0.6.0

description:
  - List firewall rules for a database cluster.
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
- name: Get database firewall rules
  digitalocean.cloud.database_firewall_rules_info:
    token: "{{ token }}"
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
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
  description: Database firewall rules result information.
  returned: always
  type: str
  sample:
    - Current database firewall rules
    - No database firewall rules
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DatabaseFirewallRulesInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            rules = self.client.databases.list_firewall_rules(
                database_cluster_uuid=self.cluster_id
            ).get("rules", [])
            if rules:
                self.module.exit_json(
                    changed=False,
                    msg="Current database firewall rules",
                    rules=rules,
                )
            self.module.exit_json(
                changed=False, msg="No database firewall rules", rules=[]
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
                rules=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    DatabaseFirewallRulesInformation(module)


if __name__ == "__main__":
    main()
