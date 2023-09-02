#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: domains_info

short_description: Retrieve a list of all of the domains in your account

version_added: 0.2.0

description:
  - Retrieve a list of all of the domains in your account.
  - View the API documentation at (https://docs.digitalocean.com/reference/api/api-reference/#operation/domains_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get domains
  digitalocean.cloud.domains_info:
    token: "{{ token }}"
"""


RETURN = r"""
domains:
  description: Domains.
  returned: always
  type: list
  elements: dict
  sample:
    - name: example.com
      ttl: 1800
      zone_file: |-
        $ORIGIN example.com.
        $TTL 1800
        example.com. IN SOA ns1.digitalocean.com. hostmaster.example.com 1657981824 10800 3600 604800 1800
        test.example.com. 300 IN A 1.2.3.4
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
    - Current domains
    - No domains
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DomainsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        try:
            domains = self.client.domains.list()
            if domains.get("domains"):
                self.module.exit_json(
                    changed=False, msg="Current domains", domains=domains.get("domains")
                )
            self.module.exit_json(changed=False, msg="No domains", domains=[])
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(changed=False, msg=error.get("Message"), error=error)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    DomainsInformation(module)


if __name__ == "__main__":
    main()
