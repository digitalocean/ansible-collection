#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: uptime_alert

short_description: Create or delete uptime check alerts

version_added: 1.9.0

description:
  - Create or delete alerts for uptime checks.
  - Alerts notify you when an uptime check fails or recovers.
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
  name:
    description:
      - The name of the alert.
    type: str
    required: true
  type:
    description:
      - The type of alert.
    type: str
    required: false
    choices:
      - latency
      - down
      - down_global
      - ssl_expiry
  threshold:
    description:
      - The threshold at which the alert triggers.
      - For latency alerts, this is in milliseconds.
      - For ssl_expiry alerts, this is in days.
    type: int
    required: false
  comparison:
    description:
      - The comparison operator for the threshold.
    type: str
    required: false
    choices:
      - greater_than
      - less_than
  notifications:
    description:
      - Notification settings for the alert.
    type: dict
    required: false
    suboptions:
      email:
        description:
          - List of email addresses to notify.
        type: list
        elements: str
      slack:
        description:
          - List of Slack webhook configurations.
        type: list
        elements: dict
  period:
    description:
      - The period of time the threshold must be breached to trigger the alert.
    type: str
    required: false
    choices:
      - 2m
      - 3m
      - 5m
      - 10m
      - 15m
      - 30m
      - 1h
  id:
    description:
      - The unique identifier of the alert.
      - Used for lookup when updating or deleting.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create uptime alert
  digitalocean.cloud.uptime_alert:
    token: "{{ token }}"
    state: present
    check_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    name: high-latency-alert
    type: latency
    threshold: 500
    comparison: greater_than
    notifications:
      email:
        - alerts@example.com
    period: 5m

- name: Delete uptime alert
  digitalocean.cloud.uptime_alert:
    token: "{{ token }}"
    state: absent
    check_id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    name: high-latency-alert
"""


RETURN = r"""
alert:
  description: Uptime alert information.
  returned: always
  type: dict
  sample:
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
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
  description: Uptime alert result information.
  returned: always
  type: str
  sample:
    - Created uptime alert high-latency-alert
    - Deleted uptime alert high-latency-alert
    - Uptime alert high-latency-alert would be created
    - Uptime alert high-latency-alert exists
    - Uptime alert high-latency-alert does not exist
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class UptimeAlert(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.check_id = module.params.get("check_id")
        self.name = module.params.get("name")
        self.alert_type = module.params.get("type")
        self.threshold = module.params.get("threshold")
        self.comparison = module.params.get("comparison")
        self.notifications = module.params.get("notifications")
        self.period = module.params.get("period")
        self.id = module.params.get("id")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_alert(self):
        try:
            alerts = self.client.uptime.list_alerts(check_id=self.check_id).get(
                "alerts", []
            )
            for alert in alerts:
                if alert.get("name") == self.name:
                    return alert
                elif self.id and alert.get("id") == self.id:
                    return alert
            return None
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
                alert={},
            )

    def create_alert(self):
        try:
            body = {
                "name": self.name,
                "type": self.alert_type,
            }
            if self.threshold is not None:
                body["threshold"] = self.threshold
            if self.comparison:
                body["comparison"] = self.comparison
            if self.notifications:
                body["notifications"] = self.notifications
            if self.period:
                body["period"] = self.period

            alert = self.client.uptime.create_alert(check_id=self.check_id, body=body)[
                "alert"
            ]

            self.module.exit_json(
                changed=True,
                msg=f"Created uptime alert {self.name}",
                alert=alert,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, alert={}
            )

    def delete_alert(self, alert):
        try:
            self.client.uptime.delete_alert(
                check_id=self.check_id, alert_id=alert["id"]
            )
            self.module.exit_json(
                changed=True,
                msg=f"Deleted uptime alert {self.name}",
                alert={},
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
                alert={},
            )

    def present(self):
        alert = self.get_alert()
        if alert is None:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Uptime alert {self.name} would be created",
                    alert={},
                )
            else:
                if not self.alert_type:
                    self.module.fail_json(
                        changed=False,
                        msg="type is required when creating an uptime alert",
                        alert={},
                    )
                self.create_alert()
        else:
            self.module.exit_json(
                changed=False,
                msg=f"Uptime alert {self.name} exists",
                alert=alert,
            )

    def absent(self):
        alert = self.get_alert()
        if alert is None:
            self.module.exit_json(
                changed=False,
                msg=f"Uptime alert {self.name} does not exist",
                alert={},
            )
        else:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Uptime alert {self.name} would be deleted",
                    alert=alert,
                )
            else:
                self.delete_alert(alert)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        check_id=dict(type="str", required=True),
        name=dict(type="str", required=True),
        type=dict(
            type="str",
            required=False,
            choices=["latency", "down", "down_global", "ssl_expiry"],
        ),
        threshold=dict(type="int", required=False),
        comparison=dict(
            type="str", required=False, choices=["greater_than", "less_than"]
        ),
        notifications=dict(type="dict", required=False),
        period=dict(
            type="str",
            required=False,
            choices=["2m", "3m", "5m", "10m", "15m", "30m", "1h"],
        ),
        id=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    UptimeAlert(module)


if __name__ == "__main__":
    main()
