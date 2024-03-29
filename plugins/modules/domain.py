#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: domain

short_description: Manage domains

version_added: 0.2.0

description:
  - |
    Domain resources are domain names that you have purchased from a domain name registrar that
    you are managing through the DigitalOcean DNS interface.
  - This module establishes top-level control over each domain.
  - Actions that affect individual domain records should be taken on the C(domain_record) module.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Domains).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - The name of the domain itself.
      - This should follow the standard domain format of domain.TLD.
      - For instance, C(example.com) is a valid domain name.
    required: true
    type: str
  ip_address:
    description:
      - This optional attribute may contain an IP address.
      - When provided, an A record will be automatically created pointing to the apex domain.
    required: false
    type: str

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create domain
  digitalocean.cloud.domain:
    token: "{{ token }}"
    name: my-test-domain.com

- name: Create domain and apex record
  digitalocean.cloud.domain:
    token: "{{ token }}"
    name: my-test-domain.com
    ip_address: 192.168.100.50
"""


RETURN = r"""
domain:
  description: Domain.
  returned: always
  type: dict
  sample:
    name: example.com
    ttl: 1800
    zone_file: |
      $ORIGIN example.com.
      $TTL 1800
      example.com. IN SOA ns1.digitalocean.com. hostmaster.example.com. 1672671168 10800 3600 604800 1800
      example.com. 1800 IN NS ns1.digitalocean.com.
      example.com. 1800 IN NS ns2.digitalocean.com.
      example.com. 1800 IN NS ns3.digitalocean.com.
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Domain result information.
  returned: always
  type: str
  sample:
    - Created domain example.com
    - Domain example.com exists
    - Domain example.com would be created
    - Domain example.com would be deleted
    - Domain example.com does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class Domain(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.ip_address = module.params.get("ip_address")
        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_domain_by_name(self):
        try:
            domains = self.client.domains.list()["domains"]
            for domain in domains:
                if domain["name"] == self.name:
                    return domain
            return None
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, domain=[]
            )

    def create_domain(self):
        try:
            body = dict(
                name=self.name,
                ip_address=self.ip_address,
            )
            domain = self.client.domains.create(body=body)["domain"]
            self.module.exit_json(
                changed=True,
                msg=f"Created domain {self.name}",
                domain=domain,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, domain=[]
            )

    def delete_domain(self):
        try:
            self.client.domains.delete(domain_name=self.name)
            self.module.exit_json(
                changed=True,
                msg=f"Deleted domain {self.name}",
                domain=[],
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, domain=[]
            )

    def present(self):
        """Creates or updates a domain."""
        found_domain = self.get_domain_by_name()
        if self.module.check_mode:
            if found_domain:
                self.module.exit_json(
                    changed=False,
                    msg=f"Domain {self.name} exists",
                    domain=found_domain,
                )
            else:
                self.module.exit_json(
                    changed=True,
                    msg=f"Domain {self.name} would be created",
                    domain=[],
                )
        if found_domain:
            self.module.exit_json(
                changed=False,
                msg=f"Domain {self.name} exists",
                domain=found_domain,
            )
        else:
            self.create_domain()

    def absent(self):
        """Removes a domain."""
        found_domain = self.get_domain_by_name()
        if self.module.check_mode:
            if found_domain:
                self.module.exit_json(
                    changed=True,
                    msg=f"Domain {self.name} would be deleted",
                    domain=found_domain,
                )
            else:
                self.module.exit_json(
                    changed=False,
                    msg=f"Domain {self.name} does not exist",
                    domain=[],
                )
        if found_domain:
            self.delete_domain()
        else:
            self.module.exit_json(
                changed=False,
                msg=f"Domain {self.name} does not exist",
                domain=found_domain,
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=True),
        ip_address=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    Domain(module)


if __name__ == "__main__":
    main()
