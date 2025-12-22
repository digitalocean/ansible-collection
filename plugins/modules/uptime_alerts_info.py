#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: uptime_alerts_info

short_description: List all alerts for an uptime check

version_added: 0.6.0

description:
  - List all alerts for an uptime check.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Uptime).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  check_id:
    description:
      - The unique identifier of the uptime check.
    type: str
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get uptime alerts
  digitalocean.cloud.uptime_alerts_info:
    token: "{{ token }}"
    check_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
"""


RETURN = r"""
alerts:
  description: Uptime alerts.
  returned: always
  type: list
  elements: dict
  sample:
    - id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      name: high-latency-alert
      type: latency
      threshold: 500
      comparison: greater_than
      notifications:
        email:
          - alerts@example.com
      period: 5m
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Uptime alerts result information.
  returned: always
  type: str
  sample:
    - Current uptime alerts
    - No uptime alerts
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class UptimeAlertsInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.check_id = module.params.get("check_id")
        if self.state == "present":
            self.present()

    def present(self):
        try:
            alerts = self.client.uptime.list_alerts(check_id=self.check_id).get(
                "alerts", []
            )
            if alerts:
                self.module.exit_json(
                    changed=False,
                    msg="Current uptime alerts",
                    alerts=alerts,
                )
            self.module.exit_json(changed=False, msg="No uptime alerts", alerts=[])
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
                alerts=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        check_id=dict(type="str", required=True),
    )
    module = AnsibleModule(argument_spec=argument_spec, supports_check_mode=True)
    UptimeAlertsInformation(module)


if __name__ == "__main__":
    main()
