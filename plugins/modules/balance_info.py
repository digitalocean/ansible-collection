#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: balance_info

short_description: Retrieve the balances on a customer's account

version_added: 0.2.0

description:
  - Retrieve the balances on a customer's account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/balance_get).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get balance information
  digitalocean.cloud.balance_info:
    token: "{{ token }}"
"""


RETURN = r"""
balance:
  description: Balance information.
  returned: always
  type: dict
  sample:
    month_to_date_balance: 23.44
    account_balance: 12.23
    month_to_date_usage: 11.21
    generated_at: '2019-07-09T15:01:12Z'
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Balance result information.
  returned: always
  type: str
  sample:
    - Current balance information
    - Current balance information not found
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class BalanceInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        try:
            balance = self.client.balance.get()
            if balance:
                self.module.exit_json(
                    changed=False, msg="Current balance information", balance=balance
                )
            self.module.fail_json(
                changed=False, msg="Current balance information not found"
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
    BalanceInformation(module)


if __name__ == "__main__":
    main()
