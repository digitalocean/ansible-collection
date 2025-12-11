#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: ssh_keys_info

short_description: List all of the keys in your account

version_added: 0.2.0

description:
  - List all of the keys in your account.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/sshKeys_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get SSH keys
  digitalocean.cloud.ssh_keys_info:
    token: "{{ token }}"
"""


RETURN = r"""
ssh_keys:
  description: SSH keys.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 289794
      fingerprint: '3b:16:e4:bf:8b:00:8b:b8:59:8c:a9:d3:f0:19:fa:45'
      public_key: 'ssh-rsa ANOTHEREXAMPLEaC1yc2EAAAADAQABAAAAQ...owLh64b72pxekALga2oi4GvT+TlWNhzPH4V anotherexample'
      name: Other Public Key
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: SSH keys result information.
  returned: always
  type: str
  sample:
    - Current SSH keys
    - No SSH keys
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanFunctions,
    DigitalOceanOptions,
)


class SSHKeysInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        if self.state == "present":
            self.present()

    def present(self):
        ssh_keys = DigitalOceanFunctions.get_paginated(
            module=self.module,
            obj=self.client.ssh_keys,
            meth="list",
            key="ssh_keys",
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        if ssh_keys:
            self.module.exit_json(
                changed=False,
                msg="Current SSH keys",
                ssh_keys=ssh_keys,
            )
        self.module.exit_json(changed=False, msg="No SSH keys", ssh_keys=[])


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    SSHKeysInformation(module)


if __name__ == "__main__":
    main()
