#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: uptime_checks_state_info

short_description: Get the state of an Uptime check

version_added: 0.5.0

description:
  - Get the state of an Uptime check.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/uptime_get_checkState).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  state:
    description: Only C(present) is supported which will return the state of the Uptime check.
    type: str
    required: false
    default: present
    choices: [present]
  check_id:
    description: The Uptime check UUID.
    type: str
    required: false
  name:
    description:
      - The Uptime check name.
      - Will fail if there is more than one check with this C(name).
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Get Uptime check state by ID
  digitalocean.cloud.uptime_checks_state_info:
    token: "{{ token }}"
    check_id: 4de7ac8b-495b-4884-9a69-1050c6793cd6

- name: Get Uptime check state by name
  digitalocean.cloud.uptime_checks_state_info:
    token: "{{ token }}"
    name: my-check
"""


RETURN = r"""
state:
  description: Uptime check state.
  returned: always
  type: dict
  elements: dict
  sample:
    state:
      regions:
        us_east:
          status: UP
          status_changed_at: "2022-03-17T22:28:51Z"
          thirty_day_uptime_percentage: 97.99
        eu_west:
           status: UP
           status_changed_at: "2022-03-17T22:28:51Z"
           thirty_day_uptime_percentag": 97.99
      previous_outage:
        region: us_east
        started_at: "2022-03-17T18:04:55Z"
        ended_at: "2022-03-17T18:06:55Z"
        duration_seconds: 120
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Uptime checks result information.
  returned: always
  type: str
  sample:
    - Current Uptime check 4de7ac8b-495b-4884-9a69-1050c6793cd6 state
    - No Uptime check 4de7ac8b-495b-4884-9a69-1050c6793cd6 state
    - No Uptime check named my-check
    - Current Uptime check named my-check state
    - Multiple Uptime checks named my-check
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class UptimeChecksStateInformation(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.check_id = self.module.params.get("check_id")
        self.name = self.module.params.get("name")
        if self.state == "present":
            self.present()

    def get_checks_matching_name(self, check_name: str):
        try:
            checks = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.uptime,
                meth="list_checks",
                key="checks",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            matches = []
            for check in checks:
                if check["name"] == check_name:
                    matches.append(check)
            return matches
        except DigitalOceanCommonModule.HttpResponseError as err:
            DigitalOceanCommonModule.http_response_error(self.module, err)

    def present(self):
        try:
            if self.check_id:
                state = self.client.uptime.get_check_state(check_id=self.check_id)
                if state:
                    self.module.exit_json(
                        changed=False,
                        msg=f"Current Uptime check {self.check_id} state",
                        state=state["state"],
                    )
                self.module.exit_json(
                    changed=False,
                    msg=f"No Uptime check {self.check_id} state",
                    state=[],
                )

            elif self.name:
                matches = self.get_checks_matching_name(check_name=self.name)

                if len(matches) == 0:
                    self.module.exit_json(
                        changed=False,
                        msg=f"No Uptime check named {self.name}",
                        state=[],
                    )

                elif len(matches) == 1:
                    state = self.client.uptime.get_check_state(
                        check_id=matches[0]["id"]
                    )["state"]
                    self.module.exit_json(
                        changed=False,
                        msg=f"Current Uptime check named {self.name} state",
                        state=state,
                    )

                self.module.fail_json(
                    changed=False,
                    msg=f"Multiple Uptime check named {self.name}",
                    state=[],
                )

        except DigitalOceanCommonModule.HttpResponseError as err:
            if err.status_code == 403:  # Handle this as "check does not exist"
                if self.check_id:
                    self.module.exit_json(
                        changed=False,
                        msg=f"No Uptime check {self.check_id}",
                        state=[],
                    )
                elif self.name:
                    self.module.exit_json(
                        changed=False,
                        msg=f"No Uptime check named {self.name}",
                        state=[],
                    )
            DigitalOceanCommonModule.http_response_error(self.module, err)


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        state=dict(type="str", default="present", choices=["present"]),
        check_id=dict(type="str", required=False),
        name=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[("check_id", "name")],
        required_one_of=[("check_id", "name")],
    )
    UptimeChecksStateInformation(module)


if __name__ == "__main__":
    main()
