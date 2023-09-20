#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: one_clicks_info

short_description: List all available 1-Click applications

version_added: 0.2.0

description:
  - List all available 1-Click applications.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/oneClicks_list).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  type:
    description:
      - Limit by type of 1-Click application.
    type: str
    required: false
    choices: [ droplet, kubernetes ]

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get 1-Click applications
  digitalocean.cloud.one_click_info:
    token: "{{ token }}"

- name: Get Droplet 1-Click applications
  digitalocean.cloud.one_click_info:
    token: "{{ token }}"
    type: droplet

- name: Get Kubernetes 1-Click applications
  digitalocean.cloud.one_click_info:
    token: "{{ token }}"
    type: kubernetes
"""


RETURN = r"""
one_clicks:
  description: DigitalOcean account information.
  returned: always
  type: list
  elements: dict
  sample:
    - slug: cpanel-cpanelwhm-7-9
      type: droplet
    - slug: npool
      type: droplet
    - slug: optimajet-workflowserver-18-04
      type: droplet
    - ...
    - slug: netdata
      type: kubernetes
    - slug: okteto
      type: kubernetes
    - slug: fyipe
      type: kubernetes
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: 1-Click applications result information.
  returned: always
  type: str
  sample:
    - Current 1-Click applications
    - Current Droplet 1-Click applications
    - Current Kubernetes 1-Click applications
    - Current 1-Click applications not found
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class OneClickApplicationsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.type = module.params.get("type")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            one_clicks_info = self.client.one_clicks.list()
            one_clicks = one_clicks_info.get("1_clicks")
            if one_clicks:
                click_type = self.module.params.get("type")
                if click_type:
                    filtered_clicks = list(
                        filter(lambda val: val.get("type") == click_type, one_clicks)
                    )
                    self.module.exit_json(
                        changed=False,
                        msg=f"Current {self.type.capitalize()} 1-Click applications",
                        one_clicks=filtered_clicks,
                    )
                self.module.exit_json(
                    changed=False,
                    msg="Current 1-Click applications",
                    one_clicks=one_clicks,
                )
            self.module.fail_json(
                changed=False, msg="Current 1-Click applications not found"
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
    argument_spec.update(
        type=dict(type="str", choices=["droplet", "kubernetes"], required=False),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    OneClickApplicationsInformation(module)


if __name__ == "__main__":
    main()
