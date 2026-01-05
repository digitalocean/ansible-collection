#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: invoices_info

short_description: List account invoices

version_added: 1.9.0

description:
  - List all invoices for your DigitalOcean account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Billing).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get account invoices
  digitalocean.cloud.invoices_info:
    token: "{{ token }}"
"""


RETURN = r"""
invoices:
  description: List of account invoices.
  returned: always
  type: list
  elements: dict
  sample:
    - invoice_uuid: 22737513-0ea7-4206-8ceb-98a575af7681
      amount: "27.13"
      invoice_period: 2020-01
invoice_preview:
  description: Preview of the upcoming invoice.
  returned: always
  type: dict
  sample:
    invoice_uuid: preview
    amount: "5.00"
    invoice_period: 2023-12
    updated_at: '2023-12-15T00:00:00Z'
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Invoices result information.
  returned: always
  type: str
  sample:
    - Current account invoices
    - No account invoices
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class InvoicesInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        try:
            invoices = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.invoices,
                meth="list",
                key="invoices",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            # Also try to get the invoice preview
            invoice_preview = {}
            try:
                response = self.client.invoices.list()
                invoice_preview = response.get("invoice_preview", {})
            except DigitalOceanCommonModule.HttpResponseError:
                pass

            if invoices:
                self.module.exit_json(
                    changed=False,
                    msg="Current account invoices",
                    invoices=invoices,
                    invoice_preview=invoice_preview,
                )
            self.module.exit_json(
                changed=False,
                msg="No account invoices",
                invoices=[],
                invoice_preview=invoice_preview,
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
                invoices=[],
                invoice_preview={},
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    InvoicesInformation(module)


if __name__ == "__main__":
    main()
