#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: uptime_check

short_description: Create or delete Uptime checks

version_added: 0.5.0

description:
  - Create or delete Uptime checks.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/uptime_create_check).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  name:
    description:
      - Required when C(state=present).
      - A human-friendly display name.
    type: str
    required: false
  unique_name:
    description:
      - When C(true) for C(state=present) the Uptime check will only be created if it is uniquely named.
      - When C(true) for C(state=absent) the Uptime check will only be deleted if it is uniquely named.
    type: bool
    required: false
    default: false
  check_id:
    description:
      - Required when C(state=absent).
      - The Uptime check UUID to delete.
    type: str
    required: false
  type:
    description:
      - Required when C(state=present).
      - The type of health check to perform.
    type: str
    required: false
    choices: [ping, http, https]
  target:
    description:
      - Required when C(state=present).
      - The endpoint to perform healthchecks on.
    type: str
    required: false
  regions:
    description:
      - Required when C(state=present).
      - An array containing the selected regions to perform healthchecks from.
    type: list
    elements: str
    required: false
    choices: [us_east, us_west, eu_west, se_asia]
  enabled:
    description:
      - Required when C(state=present).
      - A boolean value indicating whether the check is enabled/disabled.
    type: bool
    required: false
    default: true

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create Uptime ping check
  digitalocean.cloud.uptime_check:
    token: "{{ token }}"
    name: my-ping-check
    type: ping
    target: my-droplet-ip
    regions: [us_east]
    enabled: true
"""


RETURN = r"""
check:
  description: Uptime check.
  returned: always
  type: dict
  sample:
    - id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
      name: Landing page check
      type: https
      target: https://www.landingpage.com
      regions:
        - us_east
        - eu_west
      enabled: true
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
    - Would create Uptime check Landing page check
    - Created Uptime check named Landing page check (5a4981aa-9653-4bd1-bef5-d6bff52042e4)
    - Would delete Uptime check 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    - Deleted Uptime check 4981aa-9653-4bd1-bef5-d6bff52042e4
    - No Uptime check 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    - Uptime check 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    - Uptime check named Landing page check (5a4981aa-9653-4bd1-bef5-d6bff52042e4) exists
    - There are 3 Uptime checks named Landing page check
    - There are 3 Uptime checks 5a4981aa-9653-4bd1-bef5-d6bff52042e4, this should not happen
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
)


class UptimeCheck(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.name = self.module.params.get("name")
        self.unique_name = self.module.params.get("unique_name")
        self.check_id = self.module.params.get("check_id")
        self.type = self.module.params.get("type")
        self.target = self.module.params.get("target")
        self.regions = self.module.params.get("regions")
        self.enabled = self.module.params.get("enabled")

        if self.state == "present":
            if self.unique_name:
                self.present_unique_name()
            self.present_not_unique_name()

        elif self.state == "absent":
            if self.unique_name:
                self.absent_unique_name()
            self.absent_not_unique_name()

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

    def get_checks_matching_id(self, check_id: str):
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
                if check["id"] == check_id:
                    matches.append(check)
            return matches
        except DigitalOceanCommonModule.HttpResponseError as err:
            DigitalOceanCommonModule.http_response_error(self.module, err)

    def create_check(self):
        try:
            body = {
                "name": self.name,
                "type": self.type,
                "target": self.target,
                "regions": self.regions,
                "enabled": self.enabled,
            }
            check = self.client.uptime.create_check(body=body)["check"]
            self.module.exit_json(
                changed=True,
                msg=f"Created Uptime check named {self.name} ({check['id']})",
                check=check,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            DigitalOceanCommonModule.http_response_error(self.module, err)

    def delete_check(self, check_id: str):
        try:
            check = self.client.uptime.get_check(check_id=check_id)
            if check:
                if self.module.check_mode:
                    self.module.exit_json(
                        changed=True,
                        msg=f"Would delete Uptime check {check_id}",
                        check=check["check"],
                    )
                self.client.uptime.delete_check(check_id=check_id)
                self.module.exit_json(
                    changed=True,
                    msg=f"Deleted Uptime check {check_id}",
                    check=[],
                )
            self.module.exit_json(
                changed=False,
                msg=f"No Uptime check {check_id}",
                check=[],
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            if err.status_code == 403:  # Handle this as "check does not exist"
                self.module.exit_json(
                    changed=False,
                    msg=f"No Uptime check {check_id}",
                    check=[],
                )
            DigitalOceanCommonModule.http_response_error(self.module, err)

    def present_unique_name(self):
        matches = self.get_checks_matching_name(check_name=self.name)
        if len(matches) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Would create Uptime check named {self.name}",
                    check=[],
                )

            self.create_check()

        elif len(matches) == 1:
            self.module.exit_json(
                changed=False,
                msg=f"Uptime check named {self.name} ({matches[0]['id']}) exists",
                check=matches[0],
            )

        self.module.fail_json(
            changed=False,
            msg=f"There are {len(matches)} Uptime checks named {self.name}",
            check=matches,
        )

    def present_not_unique_name(self):
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Would create Uptime check named {self.name}",
                check=[],
            )

        self.create_check()

    def absent_unique_name(self):
        matches = self.get_checks_matching_name(check_name=self.name)
        if len(matches) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"No Uptime check named {self.name}",
                check=[],
            )

        elif len(matches) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Would delete Uptime check named {self.name} ({matches[0]['id']})",
                    check=matches[0],
                )

            self.delete_check(check_id=matches[0]["id"])

        self.module.fail_json(
            changed=False,
            msg=f"There are {len(matches)} Uptime checks named {self.name}",
            check=matches,
        )

    def absent_not_unique_name(self):
        matches = self.get_checks_matching_id(check_id=self.check_id)
        if len(matches) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"No Uptime check {self.check_id}",
                check=[],
            )

        elif len(matches) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"Would delete Uptime check named {matches[0]['name']} ({self.check_id})",
                    check=matches[0],
                )

            self.delete_check(check_id=self.check_id)

        self.module.fail_json(
            changed=False,
            msg=f"There are {len(matches)} Uptime checks {self.check_id}, this should not happen",
            check=matches,
        )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        name=dict(type="str", required=False),
        unique_name=dict(type="bool", required=False, default=False),
        check_id=dict(type="str", required=False),
        type=dict(type="str", required=False, choices=["ping", "http", "https"]),
        target=dict(type="str", required=False),
        regions=dict(
            type="list",
            elements="str",
            required=False,
            choices=["us_east", "us_west", "eu_west", "se_asia"],
        ),
        enabled=dict(type="bool", required=False, default=True),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_if=[
            ("state", "present", ["name", "type", "target", "regions", "enabled"]),
            ("state", "absent", ["name", "check_id"], True),
        ],
        required_one_of=[
            ("name", "check_id"),
        ],
        mutually_exclusive=[
            ("name", "check_id"),
        ],
        required_together=[
            ("unique_name", "name"),
        ],
    )
    UptimeCheck(module)


if __name__ == "__main__":
    main()
