#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: certificates_info

short_description: List all of the certificates available on your account

version_added: 0.2.0

description:
  - List all of the certificates available on your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/certificates_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get certificates
  digitalocean.cloud.certificates_info:
    token: "{{ token }}"
"""


RETURN = r"""
certificates:
  description: Certificates.
  returned: always
  type: dict
  sample:
    - id: 892071a0-bb95-49bc-8021-3afd67a210bf
      name: web-cert-01
      not_after: '2017-02-22T00:23:00Z'
      sha1_fingerprint: dfcc9f57d86bf58e321c2c6c31c7a971be244ac7
      created_at: '2017-02-08T16:02:37Z'
      dns_names: []
      state: verified
      type: custom
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Certificates result information.
  returned: always
  type: str
  sample:
    - Current certificates
    - No certificates
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class CertificatesInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        certificates = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.certificates,
            meth="list",
            key="certificates",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if certificates:
            self.module.exit_json(
                changed=False,
                msg="Current certificates",
                certificates=certificates,
            )
        self.module.exit_json(changed=False, msg="No certificates", certificates=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    CertificatesInformation(module)


if __name__ == "__main__":
    main()
