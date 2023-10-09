#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: one_click

short_description: Install Kubernetes 1-Click applications

version_added: 0.5.0

description:
  - Install Kubernetes 1-Click applications.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/oneClicks_install_kubernetes).
  - View the DigitalOcean Marketplace for available 1-Click applications at U(https://marketplace.digitalocean.com/).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  addon_slugs:
    description:
      - An array of 1-Click Application slugs to be installed to the Kubernetes cluster.
    type: list
    elements: str
    required: true
  cluster_uuid:
    description:
      - A unique ID for the Kubernetes cluster to which the 1-Click Applications will be installed.
    type: str
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Install 1-Click Applications
  digitalocean.cloud.one_click:
    token: "{{ token }}"
    addon_slugs:
      - kube-state-metrics
      - loki
    cluster_uuid: 50a994b6-c303-438f-9495-7e896cfe6b08
"""


RETURN = r"""
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: |
    The response will verify that a job has been successfully created to install a 1-Click.
    The post-installation lifecycle of a 1-Click application can be managed via the
    DigitalOcean API. For additional details specific to the 1-Click, find and view its
    DigitalOcean Marketplace page.
  returned: always
  type: str
  sample:
    - Successfully kicked off addon job.
    - Would install kube-state-metrics, loki into Kubernetes cluster 50a994b6-c303-438f-9495-7e896cfe6b08
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class OneClickApplication(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.addon_slugs = module.params.get("addon_slugs")
        self.cluster_uuid = module.params.get("cluster_uuid")
        if self.state == "present":
            self.present()

    def present(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Would install {', '.join(self.addon_slugs)} into Kubernetes cluster {self.cluster_uuid}",
            )

        try:
            body = {
                "addon_slugs": self.addon_slugs,
                "cluster_uuid": self.cluster_uuid,
            }
            one_click = self.client.one_clicks.install_kubernetes(body=body)

            self.module.exit_json(
                changed=True,
                msg=one_click["message"],
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
        addon_slugs=dict(type="list", elements="str", required=True),
        cluster_uuid=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    OneClickApplication(module)


if __name__ == "__main__":
    main()
