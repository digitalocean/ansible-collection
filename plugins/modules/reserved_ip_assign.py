#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2025, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: reserved_ip_assign

short_description: Create and/or assign a reserved IP to a Droplet

version_added: 1.3.0

description:
  - Create a reserved IP without assigning it.
  - Create a reserved IP and assign it to a Droplet.
  - Assign an existing reserved IP to a Droplet.
  - Unassign and delete a reserved IP.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#operation/assign_reserved_ip).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  state:
    description:
      - Whether the reserved IP should be assigned or deleted.
      - When C(present), the reserved IP will be created and/or assigned.
      - When C(absent), the reserved IP will be unassigned (if assigned) and then deleted.
    type: str
    required: false
    default: present
    choices:
      - present
      - absent
  reserved_ip:
    description:
      - The reserved IP address to assign or delete.
      - If not provided, a new reserved IP will be created (only when C(state=present)).
      - Required when C(state=absent).
      - Aliases C(floating_ip).
    type: str
    required: false
    aliases:
      - floating_ip
  droplet_id:
    description:
      - A unique identifier for a Droplet instance.
      - The Droplet that the reserved IP will be assigned to.
      - If provided, C(name) and C(region) are ignored.
      - Required when C(reserved_ip) is provided and C(state=present).
      - Not used when C(state=absent).
    type: int
    required: false
  name:
    description:
      - The name of the Droplet to assign the reserved IP to.
      - If provided, must be unique and given with C(region).
      - Required when C(reserved_ip) is provided and C(state=present).
      - Not used when C(state=absent).
    type: str
    required: false
  region:
    description:
      - The region slug where the Droplet is located or where the reserved IP should be created.
      - Required with C(name).
      - Required when creating an unassigned reserved IP.
      - Not used when C(state=absent).
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create a reserved IP without assigning it
  digitalocean.cloud.reserved_ip_assign:
    token: "{{ token }}"
    region: nyc3

- name: Create a reserved IP and assign it to a Droplet by ID
  digitalocean.cloud.reserved_ip_assign:
    token: "{{ token }}"
    droplet_id: 3164444

- name: Create a reserved IP and assign it to a Droplet by name and region
  digitalocean.cloud.reserved_ip_assign:
    token: "{{ token }}"
    name: example.com
    region: nyc3

- name: Assign an existing reserved IP to a Droplet by ID
  digitalocean.cloud.reserved_ip_assign:
    token: "{{ token }}"
    reserved_ip: "45.55.96.47"
    droplet_id: 3164444

- name: Assign an existing reserved IP to a Droplet by name and region
  digitalocean.cloud.reserved_ip_assign:
    token: "{{ token }}"
    reserved_ip: "45.55.96.47"
    name: example.com
    region: nyc3

- name: Unassign and delete a reserved IP
  digitalocean.cloud.reserved_ip_assign:
    token: "{{ token }}"
    reserved_ip: "45.55.96.47"
    state: absent
"""


RETURN = r"""
action:
  description: DigitalOcean action information.
  returned: when assigning or unassigning an existing reserved IP
  type: dict
  sample:
    completed_at: null
    id: 1882339039
    region:
      available: true
      features:
      - backups
      - ipv6
      - metadata
      - install_agent
      - storage
      - image_transfer
      name: New York 3
      sizes:
      - s-1vcpu-1gb
      - s-1vcpu-1gb-amd
      - s-1vcpu-1gb-intel
      - and many more
      slug: nyc3
    region_slug: nyc3
    resource_id: 45.55.96.47
    resource_type: reserved_ip
    started_at: '2023-09-03T12:59:10Z'
    status: in-progress
    type: assign
reserved_ip:
  description: Reserved IP information.
  returned: always
  type: dict
  sample:
    ip: 45.55.96.47
    droplet:
      id: 3164444
      name: example.com
    region:
      name: New York 3
      slug: nyc3
      features:
      - private_networking
      - backups
      - ipv6
      - metadata
      - install_agent
      - storage
      - image_transfer
      available: true
      sizes:
      - s-1vcpu-1gb
      - s-1vcpu-2gb
      - s-1vcpu-3gb
      - s-2vcpu-2gb
      - s-3vcpu-1gb
      - s-2vcpu-4gb
      - s-4vcpu-8gb
      - s-6vcpu-16gb
      - s-8vcpu-32gb
      - s-12vcpu-48gb
      - s-16vcpu-64gb
      - s-20vcpu-96gb
      - s-24vcpu-128gb
      - s-32vcpu-192g
    locked: false
    project_id: 746c6152-2fa2-11ed-92d3-27aaa54e4988
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: Reserved IP operation result information.
  returned: always
  type: str
  sample:
    - Created reserved IP 45.55.96.47
    - Created reserved IP 45.55.96.47 and assigned to Droplet 3164444
    - Reserved IP 45.55.96.47 assigned to Droplet 3164444
    - Reserved IP 45.55.96.47 assigned to Droplet 3164444 and it has not completed, status is 'in-progress'
    - Reserved IP 45.55.96.47 already assigned to Droplet 3164444
    - Reserved IP 45.55.96.47 unassigned from Droplet 3164444
    - Reserved IP 45.55.96.47 deleted
    - Reserved IP 45.55.96.47 not found
    - Droplet 3164444 not found
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
    DigitalOceanConstants,
)


class ReservedIPAssign(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.timeout = module.params.get("timeout")
        self.state = module.params.get("state", "present")
        self.reserved_ip = module.params.get("reserved_ip")
        self.droplet_id = module.params.get("droplet_id")
        self.name = module.params.get("name")
        self.region = module.params.get("region")

        # Validate name/region requirement together
        if self.name and not self.region:
            self.module.fail_json(
                changed=False,
                msg="name requires region",
            )
        if self.region and self.name and self.droplet_id:
            # Both name and droplet_id provided - mutually exclusive
            self.module.fail_json(
                changed=False,
                msg="droplet_id and name are mutually exclusive",
            )

        # Handle state=absent (unassign and delete)
        if self.state == "absent":
            if not self.reserved_ip:
                self.module.fail_json(
                    changed=False,
                    msg="reserved_ip is required when state=absent",
                )
            # Get reserved IP data - handle 404 gracefully for idempotency
            # Use try/except to catch 404 errors for idempotent behavior
            try:
                self.reserved_ip_data = self.client.reserved_ips.get(
                    reserved_ip=self.reserved_ip
                )["reserved_ip"]
            except KeyError:
                # If response doesn't have "reserved_ip" key, handle it
                try:
                    response = self.client.reserved_ips.get(
                        reserved_ip=self.reserved_ip
                    )
                    if isinstance(response, dict):
                        self.reserved_ip_data = response
                    else:
                        self.module.fail_json(
                            changed=False,
                            msg=f"Unexpected response format when getting reserved IP {self.reserved_ip}",
                        )
                except DigitalOceanCommonModule.HttpResponseError as err:
                    if err.status_code == 404:
                        self.module.exit_json(
                            changed=False,
                            msg=f"Reserved IP {self.reserved_ip} does not exist",
                            action=[],
                            reserved_ip=[],
                        )
                    raise
            except DigitalOceanCommonModule.HttpResponseError as err:
                # If reserved IP doesn't exist (404), that's fine - idempotent behavior
                if err.status_code == 404:
                    self.module.exit_json(
                        changed=False,
                        msg=f"Reserved IP {self.reserved_ip} does not exist",
                        action=[],
                        reserved_ip=[],
                    )
                # For other errors, fail
                error = {
                    "Message": err.error.message,
                    "Status Code": err.status_code,
                    "Reason": err.reason,
                }
                self.module.fail_json(
                    changed=False,
                    msg=error.get("Message"),
                    error=error,
                    action=[],
                    reserved_ip=[],
                )

            # Ensure reserved_ip_data is a dict before accessing it
            if not isinstance(self.reserved_ip_data, dict):
                self.module.fail_json(
                    changed=False,
                    msg=f"Unexpected reserved IP data format: {type(self.reserved_ip_data)}",
                    reserved_ip_data=self.reserved_ip_data,
                )

            # Check if reserved IP is assigned - if so, unassign it first
            if self.reserved_ip_data.get("droplet"):
                self._unassign_internal()
            # Now delete the reserved IP (whether it was assigned or not)
            self.delete()
            return

        # If reserved_ip is provided, we're assigning an existing reserved IP
        if self.reserved_ip:
            self.reserved_ip_data = self.get_reserved_ip()
            # Only proceed if reserved_ip_data was successfully retrieved
            # (get_reserved_ip() calls fail_json() if it fails, which raises SystemExit,
            # but we check here in case the exception is caught in tests)
            if self.reserved_ip_data is None:
                return
            # Check if droplet_id or name is provided (explicitly check for None/empty)
            # Handle both None and empty string cases from Ansible params
            # droplet_id can be int or None/empty string, so check type appropriately
            has_droplet_id = (
                self.droplet_id is not None
                and self.droplet_id != 0
                and (not isinstance(self.droplet_id, str) or self.droplet_id != "")
            )
            # name requires region, so check both are provided and non-empty
            has_name = (
                self.name is not None
                and self.name != ""
                and self.name.strip()
                and self.region is not None
                and self.region != ""
                and self.region.strip()
            )
            if has_droplet_id or has_name:
                self.droplet = DigitalOceanFunctions.find_droplet(
                    module=self.module,
                    client=self.client,
                    droplet_id=self.droplet_id,
                    name=self.name,
                    region=self.region,
                )
                self.assign()
            else:
                self.module.fail_json(
                    changed=False,
                    msg="Must provide either droplet_id or both name and region when assigning an existing reserved IP",
                )
        else:
            # No reserved_ip provided, so we're creating one
            if self.droplet_id or self.name:
                # Create and assign to droplet
                self.droplet = DigitalOceanFunctions.find_droplet(
                    module=self.module,
                    client=self.client,
                    droplet_id=self.droplet_id,
                    name=self.name,
                    region=self.region,
                )
                self.create_and_assign()
            else:
                # Create unassigned reserved IP - requires region
                if not self.region:
                    self.module.fail_json(
                        changed=False,
                        msg="Must provide region when creating an unassigned reserved IP",
                    )
                self.create()

    def get_reserved_ip(self):
        try:
            reserved_ip_data = self.client.reserved_ips.get(
                reserved_ip=self.reserved_ip
            )["reserved_ip"]
            return reserved_ip_data
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=f"Reserved IP {self.reserved_ip} not found",
                error=error,
                action=[],
                reserved_ip=[],
            )
            return None  # This should never be reached as fail_json raises SystemExit

    def create(self):
        """Create a reserved IP without assigning it."""
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Reserved IP would be created in {self.region}",
                action=[],
                reserved_ip=[],
            )
            return

        try:
            body = {
                "region": self.region,
            }
            reserved_ip_data = self.client.reserved_ips.create(body=body)["reserved_ip"]
            # Remove droplet field if it's None/null to match test expectations
            # The DigitalOcean API may return "droplet": null for unassigned reserved IPs,
            # but our integration tests expect the field to be absent entirely (not defined)
            # when checking "droplet is not defined". Removing None/null values ensures
            # the output is cleaner and matches the test assertion expectations.
            if reserved_ip_data.get("droplet") is None:
                reserved_ip_data.pop("droplet", None)
            self.module.exit_json(
                changed=True,
                msg=f"Created reserved IP {reserved_ip_data['ip']}",
                action=[],
                reserved_ip=reserved_ip_data,
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
                action=[],
                reserved_ip=[],
            )

    def create_and_assign(self):
        """Create a reserved IP and assign it to a Droplet."""
        droplet_id = self.droplet["id"]
        droplet_name = self.droplet["name"]
        droplet_region = self.droplet["region"]["slug"]

        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Reserved IP would be created and assigned to Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
                action=[],
                reserved_ip=[],
            )

        # Check if droplet already has a reserved IP assigned (idempotency check)
        try:
            reserved_ips = self.client.reserved_ips.list()["reserved_ips"]
            for reserved_ip in reserved_ips:
                if (
                    reserved_ip.get("droplet")
                    and reserved_ip["droplet"]["id"] == droplet_id
                ):
                    # Droplet already has a reserved IP assigned - return it (idempotent)
                    self.module.exit_json(
                        changed=False,
                        msg=f"Reserved IP {reserved_ip['ip']} already assigned to Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
                        action=[],
                        reserved_ip=reserved_ip,
                    )
                    return
        except DigitalOceanCommonModule.HttpResponseError:
            # If we can't list reserved IPs, continue with creation attempt
            pass

        try:
            body = {
                "droplet_id": droplet_id,
            }
            reserved_ip_data = self.client.reserved_ips.create(body=body)["reserved_ip"]
            self.module.exit_json(
                changed=True,
                msg=f"Created reserved IP {reserved_ip_data['ip']} and assigned to Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
                action=[],
                reserved_ip=reserved_ip_data,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            # Handle the case where droplet already has a reserved IP (422 error)
            if (
                err.status_code == 422
                and "already assigned" in err.error.message.lower()
            ):
                # Try to find the existing reserved IP for this droplet
                try:
                    reserved_ips = self.client.reserved_ips.list()["reserved_ips"]
                    for reserved_ip in reserved_ips:
                        if (
                            reserved_ip.get("droplet")
                            and reserved_ip["droplet"]["id"] == droplet_id
                        ):
                            # Found the existing reserved IP - return it (idempotent)
                            self.module.exit_json(
                                changed=False,
                                msg=f"Reserved IP {reserved_ip['ip']} already assigned to Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
                                action=[],
                                reserved_ip=reserved_ip,
                            )
                            return
                except DigitalOceanCommonModule.HttpResponseError:
                    pass  # Fall through to fail_json below

            # For other errors, fail
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                action=[],
                reserved_ip=[],
            )

    def assign(self):
        """Assign an existing reserved IP to a Droplet."""
        droplet_id = self.droplet["id"]
        droplet_name = self.droplet["name"]
        droplet_region = self.droplet["region"]["slug"]

        # Refresh reserved IP data to ensure we have the latest state
        try:
            self.reserved_ip_data = self.client.reserved_ips.get(
                reserved_ip=self.reserved_ip
            )["reserved_ip"]
        except DigitalOceanCommonModule.HttpResponseError:
            # If we can't get the reserved IP, use what we have
            pass

        # Check if already assigned to the same droplet (idempotency check)
        if self.reserved_ip_data.get("droplet"):
            if self.reserved_ip_data["droplet"]["id"] == droplet_id:
                self.module.exit_json(
                    changed=False,
                    msg=f"Reserved IP {self.reserved_ip} already assigned to Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
                    action=[],
                    reserved_ip=self.reserved_ip_data,
                )

        # Check if droplet already has a different reserved IP assigned
        try:
            reserved_ips = self.client.reserved_ips.list()["reserved_ips"]
            for reserved_ip in reserved_ips:
                if (
                    reserved_ip.get("droplet")
                    and reserved_ip["droplet"]["id"] == droplet_id
                ):
                    # Droplet has a reserved IP assigned - check if it's the same one
                    if reserved_ip["ip"] == self.reserved_ip:
                        # Same reserved IP already assigned - idempotent
                        self.module.exit_json(
                            changed=False,
                            msg=f"Reserved IP {self.reserved_ip} already assigned to Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
                            action=[],
                            reserved_ip=reserved_ip,
                        )
                    else:
                        # Different reserved IP assigned - this is an error condition
                        self.module.fail_json(
                            changed=False,
                            msg=(
                                f"Droplet {droplet_name} ({droplet_id}) is already assigned to reserved IP "
                                f"{reserved_ip['ip']}. Cannot assign {self.reserved_ip}."
                            ),
                            error={
                                "Message": f"Droplet is already assigned to another reserved IP ({reserved_ip['ip']})",
                                "Status Code": 422,
                                "Reason": "Unprocessable Entity",
                            },
                            action=[],
                            reserved_ip=[],
                        )
        except DigitalOceanCommonModule.HttpResponseError:
            # If we can't list reserved IPs, continue with assignment attempt
            pass

        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Reserved IP {self.reserved_ip} would be assigned to Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
                action=[],
                reserved_ip=self.reserved_ip_data,
            )

        try:
            body = {
                "type": "assign",
                "droplet_id": droplet_id,
            }
            # Based on DigitalOcean API: POST /v2/reserved_ips/{ip}/actions
            # See: https://docs.digitalocean.com/reference/api/digitalocean/#tag/Reserved-IP-Actions/operation/reservedIPsActions_post
            action = self.client.reserved_ips_actions.post(
                reserved_ip=self.reserved_ip, body=body
            )["action"]

            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and action["status"] != "completed":
                time.sleep(DigitalOceanConstants.SLEEP)
                action = self.get_action_by_id(action_id=action["id"])

            if action["status"] != "completed":
                self.module.fail_json(
                    changed=True,
                    msg=(
                        f"Reserved IP {self.reserved_ip} assigned to Droplet {droplet_name} ({droplet_id}) in {droplet_region} "
                        f"and it has not completed, status is '{action['status']}'"
                    ),
                    action=action,
                    reserved_ip=self.reserved_ip_data,
                )

            # Refresh reserved IP data after assignment
            try:
                reserved_ip_data = self.client.reserved_ips.get(
                    reserved_ip=self.reserved_ip
                )["reserved_ip"]
            except DigitalOceanCommonModule.HttpResponseError:
                reserved_ip_data = self.reserved_ip_data

            self.module.exit_json(
                changed=True,
                msg=f"Reserved IP {self.reserved_ip} assigned to Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
                action=action,
                reserved_ip=reserved_ip_data,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            # Handle the case where droplet already has a reserved IP (422 error)
            if (
                err.status_code == 422
                and "already assigned" in err.error.message.lower()
            ):
                # Try to find the existing reserved IP for this droplet
                try:
                    reserved_ips = self.client.reserved_ips.list()["reserved_ips"]
                    for reserved_ip in reserved_ips:
                        if (
                            reserved_ip.get("droplet")
                            and reserved_ip["droplet"]["id"] == droplet_id
                        ):
                            # Check if it's the same reserved IP we're trying to assign
                            if reserved_ip["ip"] == self.reserved_ip:
                                # Same reserved IP already assigned - idempotent
                                self.module.exit_json(
                                    changed=False,
                                    msg=f"Reserved IP {self.reserved_ip} already assigned to Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
                                    action=[],
                                    reserved_ip=reserved_ip,
                                )
                                return
                            else:
                                # Different reserved IP assigned - error condition
                                self.module.fail_json(
                                    changed=False,
                                    msg=(
                                        f"Droplet {droplet_name} ({droplet_id}) is already assigned to reserved IP "
                                        f"{reserved_ip['ip']}. Cannot assign {self.reserved_ip}."
                                    ),
                                    error={
                                        "Message": err.error.message,
                                        "Status Code": err.status_code,
                                        "Reason": err.reason,
                                    },
                                    action=[],
                                    reserved_ip=[],
                                )
                                return
                except DigitalOceanCommonModule.HttpResponseError:
                    pass  # Fall through to fail_json below

            # For other errors, fail
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False,
                msg=error.get("Message"),
                error=error,
                action=[],
                reserved_ip=[],
            )

    def _unassign_internal(self):
        """Internal method to unassign a reserved IP from its Droplet without exiting.

        Returns:
            dict: The action object from the unassign operation.
        """
        droplet_id = self.reserved_ip_data["droplet"]["id"]
        droplet_name = self.reserved_ip_data["droplet"]["name"]
        # Get region from reserved IP data, not droplet (droplet may not have region in response)
        droplet_region = self.reserved_ip_data.get("region", {}).get("slug", "unknown")

        if self.module.check_mode:
            return None

        try:
            body = {
                "type": "unassign",
            }
            # Based on DigitalOcean API: POST /v2/reserved_ips/{ip}/actions
            # See: https://docs.digitalocean.com/reference/api/digitalocean/#tag/Reserved-IP-Actions/operation/reservedIPsActions_post
            action = self.client.reserved_ips_actions.post(
                reserved_ip=self.reserved_ip, body=body
            )["action"]

            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time and action["status"] != "completed":
                time.sleep(DigitalOceanConstants.SLEEP)
                action = self.get_action_by_id(action_id=action["id"])

            if action["status"] != "completed":
                self.module.fail_json(
                    changed=True,
                    msg=(
                        f"Reserved IP {self.reserved_ip} unassigned from Droplet {droplet_name} ({droplet_id}) in {droplet_region} "
                        f"but it has not completed, status is '{action['status']}'"
                    ),
                    action=action,
                    reserved_ip=self.reserved_ip_data,
                )

            # Refresh reserved IP data after unassignment
            try:
                reserved_ip_data = self.client.reserved_ips.get(
                    reserved_ip=self.reserved_ip
                )["reserved_ip"]
                # Remove droplet field if it's None/null to match test expectations
                if reserved_ip_data.get("droplet") is None:
                    reserved_ip_data.pop("droplet", None)
                # Update self.reserved_ip_data for subsequent operations
                self.reserved_ip_data = reserved_ip_data
            except DigitalOceanCommonModule.HttpResponseError:
                # If we can't refresh, update the data structure to remove droplet
                if self.reserved_ip_data.get("droplet") is not None:
                    self.reserved_ip_data.pop("droplet", None)

            return action

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
                action=[],
                reserved_ip=[],
            )

    def unassign(self):
        """Unassign a reserved IP from its Droplet."""
        droplet_id = self.reserved_ip_data["droplet"]["id"]
        droplet_name = self.reserved_ip_data["droplet"]["name"]
        # Get region from reserved IP data, not droplet (droplet may not have region in response)
        droplet_region = self.reserved_ip_data.get("region", {}).get("slug", "unknown")

        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Reserved IP {self.reserved_ip} would be unassigned from Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
                action=[],
                reserved_ip=self.reserved_ip_data,
            )

        # Call internal method to do the unassignment
        action = self._unassign_internal()

        # Refresh reserved IP data for return value
        try:
            reserved_ip_data = self.client.reserved_ips.get(
                reserved_ip=self.reserved_ip
            )["reserved_ip"]
            # Remove droplet field if it's None/null to match test expectations
            if reserved_ip_data.get("droplet") is None:
                reserved_ip_data.pop("droplet", None)
        except DigitalOceanCommonModule.HttpResponseError:
            reserved_ip_data = self.reserved_ip_data
            if reserved_ip_data.get("droplet") is None:
                reserved_ip_data.pop("droplet", None)

        self.module.exit_json(
            changed=True,
            msg=f"Reserved IP {self.reserved_ip} unassigned from Droplet {droplet_name} ({droplet_id}) in {droplet_region}",
            action=action if action is not None else [],
            reserved_ip=reserved_ip_data,
        )

    def delete(self):
        """Delete a reserved IP."""
        if self.module.check_mode:
            self.module.exit_json(
                changed=True,
                msg=f"Reserved IP {self.reserved_ip} would be deleted",
                action=[],
                reserved_ip=self.reserved_ip_data,
            )

        try:
            # Based on DigitalOcean API: DELETE /v2/reserved_ips/{ip}
            # See: https://docs.digitalocean.com/reference/api/digitalocean/#tag/Reserved-IPs/operation/reservedIPs_delete
            self.client.reserved_ips.delete(reserved_ip=self.reserved_ip)
            self.module.exit_json(
                changed=True,
                msg=f"Reserved IP {self.reserved_ip} deleted",
                action=[],
                reserved_ip=[],
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
                action=[],
                reserved_ip=[],
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        state=dict(
            type="str", required=False, default="present", choices=["present", "absent"]
        ),
        reserved_ip=dict(type="str", required=False, aliases=["floating_ip"]),
        droplet_id=dict(type="int", required=False),
        name=dict(type="str", required=False),
        region=dict(type="str", required=False),
    )

    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        mutually_exclusive=[("droplet_id", "name")],
        required_if=[
            ("state", "absent", ("reserved_ip",)),
        ],
        # Note: name requires region, but region can be used alone when creating unassigned reserved IP
        # We validate this manually in the module code
    )
    ReservedIPAssign(module)


if __name__ == "__main__":
    main()
