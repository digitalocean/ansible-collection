#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2026, DigitalOcean Engineering <digitalocean-engineering-noreply@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
---
module: app

short_description: Create or delete App Platform applications

version_added: 1.9.0

description:
  - Create, update, or delete App Platform applications.
  - |
    App Platform is a Platform-as-a-Service (PaaS) offering that allows
    developers to publish code directly to DigitalOcean servers without
    worrying about the underlying infrastructure.
  - View the API documentation at U(https://docs.digitalocean.com/reference/api/api-reference/#tag/Apps).

author: Mark Mercado (@mamercad)

requirements:
  - pydo >= 0.1.3
  - azure-core >= 1.26.1

options:
  spec:
    description:
      - The app specification that describes the app.
      - This is a dictionary containing the app's components, services, etc.
    type: dict
    required: false
    suboptions:
      name:
        description:
          - The name of the app.
        type: str
      region:
        description:
          - The slug form of the geographical origin of the app.
        type: str
      services:
        description:
          - A list of services defined for the app.
        type: list
        elements: dict
      static_sites:
        description:
          - A list of static sites defined for the app.
        type: list
        elements: dict
      workers:
        description:
          - A list of workers defined for the app.
        type: list
        elements: dict
      jobs:
        description:
          - A list of jobs defined for the app.
        type: list
        elements: dict
      databases:
        description:
          - A list of databases defined for the app.
        type: list
        elements: dict
  id:
    description:
      - The unique identifier of the app.
      - Used for lookup when updating or deleting.
    type: str
    required: false
  name:
    description:
      - The name of the app to look up.
      - Used for lookup when updating or deleting.
    type: str
    required: false

extends_documentation_fragment:
  - digitalocean.cloud.common.documentation
"""


EXAMPLES = r"""
- name: Create an App Platform application
  digitalocean.cloud.app:
    token: "{{ token }}"
    state: present
    spec:
      name: my-app
      region: nyc
      services:
        - name: web
          github:
            repo: my-org/my-repo
            branch: main
          run_command: npm start
          http_port: 8080
          instance_count: 1
          instance_size_slug: basic-xxs

- name: Delete an App Platform application by name
  digitalocean.cloud.app:
    token: "{{ token }}"
    state: absent
    name: my-app

- name: Delete an App Platform application by ID
  digitalocean.cloud.app:
    token: "{{ token }}"
    state: absent
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
"""


RETURN = r"""
app:
  description: App Platform application information.
  returned: always
  type: dict
  sample:
    id: 5a4981aa-9653-4bd1-bef5-d6bff52042e4
    spec:
      name: my-app
      region: nyc
      services:
        - name: web
          github:
            repo: my-org/my-repo
            branch: main
    default_ingress: https://my-app-xxxxx.ondigitalocean.app
    created_at: '2020-03-13T19:20:47.442049222Z'
    updated_at: '2020-03-13T19:20:47.442049222Z'
    active_deployment:
      id: deployment-id
      phase: ACTIVE
error:
  description: DigitalOcean API error.
  returned: failure
  type: dict
  sample:
    Message: Informational error message.
    Reason: Unauthorized
    Status Code: 401
msg:
  description: App result information.
  returned: always
  type: str
  sample:
    - Created app my-app
    - Updated app my-app
    - Deleted app my-app
    - App my-app would be created
    - App my-app exists
"""

import time
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
    DigitalOceanOptions,
    DigitalOceanFunctions,
    DigitalOceanConstants,
)


class App(DigitalOceanCommonModule):
    def __init__(self, module):
        super().__init__(module)
        self.spec = module.params.get("spec")
        self.id = module.params.get("id")
        self.name = module.params.get("name")

        if self.state == "present":
            self.present()
        elif self.state == "absent":
            self.absent()

    def get_apps(self):
        try:
            apps = DigitalOceanFunctions.get_paginated(
                module=self.module,
                obj=self.client.apps,
                meth="list",
                key="apps",
                exc=DigitalOceanCommonModule.HttpResponseError,
            )
            found_apps = []
            for app in apps:
                app_spec = app.get("spec", {})
                if self.name and self.name == app_spec.get("name"):
                    found_apps.append(app)
                elif self.id and self.id == app.get("id"):
                    found_apps.append(app)
                elif (
                    self.spec
                    and self.spec.get("name")
                    and self.spec.get("name") == app_spec.get("name")
                ):
                    found_apps.append(app)
            return found_apps
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
                app={},
            )

    def create_app(self):
        try:
            body = {
                "spec": self.spec,
            }
            app = self.client.apps.create(body=body)["app"]

            app_id = app["id"]

            # Wait for the app to be deployed
            end_time = time.monotonic() + self.timeout
            while time.monotonic() < end_time:
                active_deployment = app.get("active_deployment", {})
                phase = active_deployment.get("phase", "").upper()
                if phase == "ACTIVE":
                    break
                if phase in ["ERROR", "FAILED"]:
                    self.module.fail_json(
                        changed=True,
                        msg=f"App deployment failed with phase: {phase}",
                        app=app,
                    )
                time.sleep(DigitalOceanConstants.SLEEP)
                try:
                    app = self.client.apps.get(id=app_id)["app"]
                except DigitalOceanCommonModule.HttpResponseError:
                    pass

            app_name = app.get("spec", {}).get("name", app_id)
            final_phase = app.get("active_deployment", {}).get("phase", "").upper()
            if final_phase != "ACTIVE":
                self.module.fail_json(
                    changed=True,
                    msg=(
                        f"App {app_name} did not become 'ACTIVE' "
                        f"within {self.timeout} seconds (current phase: {final_phase})"
                    ),
                    app=app,
                )

            self.module.exit_json(
                changed=True,
                msg=f"Created app {app_name}",
                app=app,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, app={}
            )

    def update_app(self, app):
        try:
            body = {
                "spec": self.spec,
            }
            updated_app = self.client.apps.update(id=app["id"], body=body)["app"]

            app_name = updated_app.get("spec", {}).get("name", updated_app["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Updated app {app_name}",
                app=updated_app,
            )
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, app={}
            )

    def delete_app(self, app):
        try:
            self.client.apps.delete(id=app["id"])
            app_name = app.get("spec", {}).get("name", app["id"])
            self.module.exit_json(
                changed=True,
                msg=f"Deleted app {app_name}",
                app=app,
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
                app={},
            )

    def present(self):
        apps = self.get_apps()
        app_name = (
            self.name
            or (self.spec.get("name") if self.spec else None)
            or self.id
            or "unknown"
        )

        if len(apps) == 0:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"App {app_name} would be created",
                    app={},
                )
            else:
                if not self.spec:
                    self.module.fail_json(
                        changed=False,
                        msg="spec is required when creating an app",
                        app={},
                    )
                self.create_app()
        elif len(apps) == 1:
            if self.spec:
                if self.module.check_mode:
                    self.module.exit_json(
                        changed=True,
                        msg=f"App {app_name} would be updated",
                        app=apps[0],
                    )
                else:
                    self.update_app(apps[0])
            else:
                self.module.exit_json(
                    changed=False,
                    msg=f"App {app_name} exists",
                    app=apps[0],
                )
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(apps)} apps matching {app_name}",
                app={},
            )

    def absent(self):
        apps = self.get_apps()
        app_name = (
            self.name
            or (self.spec.get("name") if self.spec else None)
            or self.id
            or "unknown"
        )

        if len(apps) == 0:
            self.module.exit_json(
                changed=False,
                msg=f"App {app_name} does not exist",
                app={},
            )
        elif len(apps) == 1:
            if self.module.check_mode:
                self.module.exit_json(
                    changed=True,
                    msg=f"App {app_name} would be deleted",
                    app=apps[0],
                )
            else:
                self.delete_app(app=apps[0])
        else:
            self.module.exit_json(
                changed=False,
                msg=f"There are currently {len(apps)} apps matching {app_name}",
                app={},
            )


def main():
    argument_spec = DigitalOceanOptions.argument_spec()
    argument_spec.update(
        spec=dict(type="dict", required=False),
        id=dict(type="str", required=False),
        name=dict(type="str", required=False),
    )
    module = AnsibleModule(
        argument_spec=argument_spec,
        supports_check_mode=True,
        required_one_of=[
            ("spec", "id", "name"),
        ],
    )
    App(module)


if __name__ == "__main__":
    main()
