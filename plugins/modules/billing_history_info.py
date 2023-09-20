#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: billing_history_info

short_description: Retrieve a list of all billing history entries

version_added: 0.2.0

description:
  - Retrieve a list of all billing history entries.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/billingHistory_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get billing history information
  digitalocean.cloud.billing_history_info:
    token: "{{ token }}"
"""


RETURN = r"""
billing_history:
  description: Billing history information.
  returned: always
  type: list
  sample:
    - description: Invoice for May 2018
      amount: 12.34
      invoice_id: 123
      invoice_uuid: example-uuid
      date: '2018-06-01T08:44:38Z'
      type: Invoice
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Billing history result information.
  returned: always
  type: str
  sample:
    - Current billing history information
    - No billing history information
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class BillingHistoryInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        try:
            billing_history = self.client.billing_history.list()
            billing_history_info = billing_history.get("billing_history")
            if billing_history_info:
                self.module.exit_json(
                    changed=False,
                    msg="Current billing history information",
                    billing_history_info=billing_history_info,
                )
            self.module.exit_json(
                changed=False,
                msg="No billing history information",  # Possibly no charges or a free account
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
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    BillingHistoryInformation(module)


if __name__ == "__main__":
    main()
