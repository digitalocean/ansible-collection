#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: invoice_items_info

short_description: Get invoice items by UUID

version_added: 0.6.0

description:
  - Get the line items for a specific invoice.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Billing).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  invoice_uuid:
    description:
      - The UUID of the invoice to retrieve items for.
    type: str
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get invoice items
  digitalocean.cloud.invoice_items_info:
    token: "{{ token }}"
    invoice_uuid: 22737513-0ea7-4206-8ceb-98a575af7681
"""


RETURN = r"""
invoice_items:
  description: List of items in the invoice.
  returned: always
  type: list
  elements: dict
  sample:
    - product: Droplets
      resource_uuid: 9c42d3e4-e6d8-45d7-a76b-9e1c5f2a4b3c
      resource_id: "123456789"
      group_description: Droplet (1 vCPU, 1GB / 25GB Disk)
      description: my-droplet
      amount: "5.00"
      duration: 744 Hours
      duration_unit: Hours
      start_time: '2023-01-01T00:00:00Z'
      end_time: '2023-02-01T00:00:00Z'
      project_name: Default
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Invoice items result information.
  returned: always
  type: str
  sample:
    - Invoice items for 22737513-0ea7-4206-8ceb-98a575af7681
    - No invoice items
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class InvoiceItemsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.invoice_uuid = module.params.get("invoice_uuid")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            invoice_items = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.invoices,
                meth="get_by_uuid",
                key="invoice_items",
                exc=DigitalOceanCommonModule.HttpResponseError,
                invoice_uuid=self.invoice_uuid,
            )
            if invoice_items:
                self.module.exit_json(
                    changed=False,
                    msg=f"Invoice items for {self.invoice_uuid}",
                    invoice_items=invoice_items,
                )
            self.module.exit_json(
                changed=False,
                msg="No invoice items",
                invoice_items=[],
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
                invoice_items=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        invoice_uuid=dict(type="str", required=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    InvoiceItemsInformation(module)


if __name__ == "__main__":
    main()
