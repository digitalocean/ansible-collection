#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: domain_records_info

short_description: Retrieve a listing of all of the domain records for a domain

version_added: 0.2.0

description:
  - Retrieve a listing of all of the domain records for a domain.
  - View the API documentation at (https://docs.digitalocean.com/reference/api/api-reference/#operation/domains_list_records).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  domain_name:
    description: The name of the domain itself.
    type: str
    required: true
  name:
    description: Retrieve a specific fully qualified record name.
    type: str
    required: false
  type:
    description: Retrieve a specific type of record.
    type: str
    required: false
    choices: [A, AAAA, CNAME, MX, TXT, SRV, NS, CAA]

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get domain records
  digitalocean.cloud.domain_records_info:
    token: "{{ token }}"
    domain_name: example.com
"""


RETURN = r"""
domain_records:
  description: Domain records.
  returned: always
  type: list
  elements: dict
  sample:
    - data: 'ns1.digitalocean.com'
      flags: null
      id: 324538538
      name: '@'
      port: null
      priority: null
      tag: null
      ttl: 1800
      type: NS
      weight: null
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Domain records result information.
  returned: always
  type: str
  sample:
    - Current domains
    - No domains
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DomainRecordsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.domain_name = module.params.get("domain_name")
        self.name = module.params.get("name")
        self.type = module.params.get("type")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            domain_records = self.client.domains.list_records(
                domain_name=self.domain_name,
                name=self.name,
                type=self.type,
            )
            if domain_records.get("domain_records"):
                self.module.exit_json(
                    changed=False,
                    msg="Current domain records",
                    domain_records=domain_records.get("domain_records"),
                )
            self.module.exit_json(
                changed=False, msg="No domain records", domain_records=[]
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, domain_records=[]
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        domain_name=dict(type="str", required=True),
        name=dict(type="str", required=False),
        type=dict(
            type="str",
            choices=["A", "AAAA", "CNAME", "MX", "TXT", "SRV", "NS", "CAA"],
            required=False,
        ),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    DomainRecordsInformation(module)


if __name__ == "__main__":
    main()
