#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: database_maintenance_window

short_description: Configure database cluster maintenance window

version_added: 1.9.0

description:
  - Configure the maintenance window for a database cluster.
  - |
    The maintenance window specifies when DigitalOcean will perform updates
    and maintenance on your database cluster.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Databases).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  cluster_id:
    description:
      - The UUID of the database cluster.
    type: str
    required: true
  day:
    description:
      - The day of the week for the maintenance window.
    type: str
    required: true
    choices:
      - monday
      - tuesday
      - wednesday
      - thursday
      - friday
      - saturday
      - sunday
  hour:
    description:
      - The hour of the day for the maintenance window (in UTC, 24-hour format).
    type: str
    required: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Set database maintenance window
  digitalocean.cloud.database_maintenance_window:
    token: "{{ token }}"
    state: present
    cluster_id: 9cc10173-e9ea-4176-9dbc-a4cee4c4ff30
    day: sunday
    hour: "03:00"
"""


RETURN = r"""
maintenance_window:
  description: Database maintenance window configuration.
  returned: always
  type: dict
  sample:
    day: sunday
    hour: "03:00"
    pending: false
    description: []
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Database maintenance window result information.
  returned: always
  type: str
  sample:
    - Updated database maintenance window
    - Database maintenance window would be updated
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
)


class DatabaseMaintenanceWindow(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.cluster_id = module.params.get("cluster_id")
        self.day = module.params.get("day")
        self.hour = module.params.get("hour")

        if self.state == "present":
            self.present()

    def update_maintenance_window(self):
        try:
            body = {
                "day": self.day,
                "hour": self.hour,
            }
            self.client.databases.update_maintenance_window(
                database_cluster_uuid=self.cluster_id, body=body
            )

            # Get the updated cluster to return maintenance window
            cluster = self.client.databases.get_cluster(
                database_cluster_uuid=self.cluster_id
            ).get("database", {})
            maintenance_window = cluster.get("maintenance_window", {})

            self.module.exit_json(
                changed=True,
                msg="Updated database maintenance window",
                maintenance_window=maintenance_window,
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
                maintenance_window={},
            )

    def present(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg="Database maintenance window would be updated",
                maintenance_window={},
            )
        else:
            self.update_maintenance_window()


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        cluster_id=dict(type="str", required=True),
        day=dict(
            type="str",
            required=True,
            choices=[
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
            ],
        ),
        hour=dict(type="str", required=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
    )
    DatabaseMaintenanceWindow(module)


if __name__ == "__main__":
    main()
