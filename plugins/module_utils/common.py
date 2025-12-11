# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import traceback

from ansible.module_utils.basic import env_fallback, missing_required_lib
from ansible.module_utils.six.moves.urllib.parse import parse_qs, urlparse


class DigitalOceanFunctions:
    @staticmethod
    def get_paginated(module, obj, meth, key, exc, params=None, **kwargs):
        results = []
        page = 1
        paginated = True
        while paginated:
            try:
                fn = getattr(obj, meth)
                resp = fn(
                    per_page=DigitalOceanConstants.PAGE_SIZE,
                    page=page,
                    params=params,
                    **kwargs,
                )
                if key:
                    if resp.get(key):
                        results.extend(resp.get(key))
                else:
                    results.extend(resp)
                links = resp.get("links")
                if links:
                    pages = links.get("pages")
                    if pages:
                        next_page = pages.get("next")
                        if next_page:
                            parsed_url = urlparse(pages["next"])
                            page = parse_qs(parsed_url.query)["page"][0]
                        else:
                            paginated = False
                    else:
                        paginated = False
                else:
                    paginated = False
            except exc as err:
                error = {
                    "Message": err.error.message,
                    "Status Code": err.status_code,
                    "Reason": err.reason,
                }
                if module:
                    module.fail_json(
                        changed=False, msg=error.get("Message"), error=error
                    )
                raise RuntimeError(error.get("Message"))
        return results

    @staticmethod
    def get_volumes_by_region(module, client, region):
        volumes = DigitalOceanFunctions.get_paginated(
            module=module,
            obj=client.volumes,
            meth="list",
            key="volumes",
            params=None,
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        found_volumes = []
        for volume in volumes:
            volume_region = volume["region"]["slug"]
            if volume_region == region:
                found_volumes.append(volume)
        return found_volumes

    @staticmethod
    def get_droplets_by_region(module, client, region):
        droplets = DigitalOceanFunctions.get_paginated(
            module=module,
            obj=client.droplets,
            meth="list",
            key="droplets",
            params=None,
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        found_droplets = []
        for droplet in droplets:
            droplet_region = droplet["region"]["slug"]
            if droplet_region == region:
                found_droplets.append(droplet)
        return found_droplets

    @staticmethod
    def get_droplet_by_name_in_region(module, client, region, name):
        droplets = DigitalOceanFunctions.get_paginated(
            module=module,
            obj=client.droplets,
            meth="list",
            key="droplets",
            params=None,
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        found_droplets = []
        for droplet in droplets:
            droplet_region = droplet["region"]["slug"]
            if droplet_region == region:
                if name == droplet["name"]:
                    found_droplets.append(droplet)
        return found_droplets

    @staticmethod
    def get_volume_by_name_in_region(module, client, region, name):
        volumes = DigitalOceanFunctions.get_paginated(
            module=module,
            obj=client.volumes,
            meth="list",
            key="volumes",
            params=None,
            exc=DigitalOceanCommonModule.HttpResponseError,
        )
        found_volumes = []
        for volume in volumes:
            volume_region = volume["region"]["slug"]
            if volume_region == region:
                if name == volume["name"]:
                    found_volumes.append(volume)
        return found_volumes

    @staticmethod
    def find_droplet(module, client, droplet_id=None, name=None, region=None):
        """Find a Droplet by ID or by name and region.

        Args:
            module: The Ansible module instance
            client: The DigitalOcean client instance
            droplet_id: Optional droplet ID to find by
            name: Optional droplet name (requires region)
            region: Optional region slug (requires name)

        Returns:
            dict: The droplet data

        Raises:
            SystemExit: If droplet not found or multiple found
        """
        if droplet_id:
            try:
                droplet = client.droplets.get(droplet_id=droplet_id)["droplet"]
                if droplet:
                    return droplet
                module.fail_json(
                    changed=False,
                    msg=f"No Droplet with ID {droplet_id}",
                )
            except DigitalOceanCommonModule.HttpResponseError as err:
                error = {
                    "Message": err.error.message,
                    "Status Code": err.status_code,
                    "Reason": err.reason,
                }
                module.fail_json(
                    changed=False,
                    msg=f"No Droplet with ID {droplet_id}",
                    error=error,
                )
        elif name and region:
            try:
                droplets = DigitalOceanFunctions.get_droplet_by_name_in_region(
                    module=module,
                    client=client,
                    region=region,
                    name=name,
                )
                if len(droplets) == 0:
                    module.fail_json(
                        changed=False,
                        msg=f"No Droplet named {name} in {region}",
                    )
                elif len(droplets) > 1:
                    droplet_ids = ", ".join(
                        [str(droplet["id"]) for droplet in droplets]
                    )
                    module.fail_json(
                        changed=False,
                        msg=f"There are currently {len(droplets)} Droplets named {name} in {region}: {droplet_ids}",
                        droplet=[],
                    )
                return droplets[0]
            except DigitalOceanCommonModule.HttpResponseError as err:
                error = {
                    "Message": err.error.message,
                    "Status Code": err.status_code,
                    "Reason": err.reason,
                }
                module.fail_json(
                    changed=False,
                    msg=f"Error finding Droplet named {name} in {region}",
                    error=error,
                )

        module.fail_json(
            changed=False,
            msg="Must provide either droplet_id or both name and region",
        )


class DigitalOceanConstants:
    PAGE_SIZE = 10
    SLEEP = 10


class DigitalOceanOptions:
    @staticmethod
    def argument_spec():
        return dict(
            state=dict(
                type="str",
                choices=["present", "absent"],
                default="present",
            ),
            timeout=dict(
                type="int",
                default=300,  # 5 minutes
            ),
            token=dict(
                type="str",
                fallback=(
                    env_fallback,
                    [
                        "DIGITALOCEAN_ACCESS_TOKEN",  # Parity with doctl
                        "DIGITALOCEAN_TOKEN",
                        "DO_API_TOKEN",
                        "DO_API_KEY",
                        "DO_OAUTH_TOKEN",
                        "OAUTH_TOKEN",
                    ],
                ),
                no_log=True,
                required=False,
                aliases=["oauth_token", "api_token"],
            ),
            client_override_options=dict(type="dict", required=False),
            module_override_options=dict(type="dict", required=False),
        )


class DigitalOceanReqs:
    HAS_AZURE_LIBRARY = False
    AZURE_LIBRARY_IMPORT_ERROR = None
    # Expose HttpResponseError as a class attribute so it can be accessed as
    # DigitalOceanCommonModule.HttpResponseError in exception handlers
    HttpResponseError = None
    try:
        from azure.core.exceptions import (
            HttpResponseError as _HttpResponseError,
        )
    except ImportError:
        AZURE_LIBRARY_IMPORT_ERROR = traceback.format_exc()
    else:
        HAS_AZURE_LIBRARY = True
        HttpResponseError = _HttpResponseError

    HAS_PYDO_LIBRARY = False
    PYDO_LIBRARY_IMPORT_ERROR = None
    try:
        from pydo import Client  # pylint: disable=unused-import
    except ImportError:
        PYDO_LIBRARY_IMPORT_ERROR = traceback.format_exc()
    else:
        HAS_PYDO_LIBRARY = True

    HAS_BOTO3_LIBRARY = False
    BOTO3_LIBRARY_IMPORT_ERROR = None
    try:
        import boto3  # pylint: disable=unused-import

        HAS_BOTO3_LIBRARY = True
    except ImportError:
        BOTO3_LIBRARY_IMPORT_ERROR = traceback.format_exc()


class DigitalOceanCommonModule(DigitalOceanReqs):
    def __init__(self, module):
        self.module = module

        if DigitalOceanReqs.AZURE_LIBRARY_IMPORT_ERROR:
            module.fail_json(msg=missing_required_lib("azure.core.exceptions"))

        if DigitalOceanReqs.PYDO_LIBRARY_IMPORT_ERROR:
            module.fail_json(msg=missing_required_lib("pydo"))

        if DigitalOceanReqs.BOTO3_LIBRARY_IMPORT_ERROR:
            module.fail_json(msg=missing_required_lib("boto3"))

        self.module_override_options = module.params.get("module_override_options")
        self.client_options = {"token": module.params.get("token")}
        self.client_override_options = module.params.get("client_override_options")
        if self.client_override_options:
            self.client_options.update(**self.client_override_options)
        self.client = DigitalOceanReqs.Client(**self.client_options)
        self.state = module.params.get("state")

    def get_action_by_id(self, action_id):
        """Get an action by its ID from the DigitalOcean API."""
        try:
            action = self.client.actions.get(action_id=action_id)["action"]
            return action
        except DigitalOceanCommonModule.HttpResponseError as err:
            error = {
                "Message": err.error.message,
                "Status Code": err.status_code,
                "Reason": err.reason,
            }
            self.module.fail_json(
                changed=False, msg=error.get("Message"), error=error, action=[]
            )

    @staticmethod
    def http_response_error(module, err: dict) -> None:
        error = {
            "Message": err.error.message,
            "Status Code": err.status_code,
            "Reason": err.reason,
        }
        module.fail_json(changed=False, msg=error.get("Message"), error=error, check=[])


class DigitalOceanCommonInventory(DigitalOceanReqs):
    def __init__(self, config):
        token = (
            config.get("token") or config.get("oauth_token") or config.get("api_token")
        )
        self.client_options = {"token": token}
        self.client_override_options = config.get("client_override_options")
        if self.client_override_options:
            self.client_options.update(**self.client_override_options)
        self.client = DigitalOceanReqs.Client(**self.client_options)


class DigitalOceanLogfile:
    def __init__(self, filename: str = "/tmp/ansible.log") -> None:
        self.filename = filename
        self.fh = open(self.filename, mode="a+", encoding="utf-8")

    def write(self, line) -> None:
        self.fh.write(line + "\n")
        self.fh.flush()

    def __del__(self) -> None:
        self.fh.close()
