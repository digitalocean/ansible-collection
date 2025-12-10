# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = r"""
name: droplets
author:
  - Mark Mercado (@mamercad)
short_description: Droplets dynamic inventory plugin
version_added: "0.4.0"
description:
  - Droplets dynamic inventory plugin.
extends_documentation_fragment:
  - constructed
  - inventory_cache
options:
  plugin:
    description:
      - The name of the this inventory plugin C(digitalocean.cloud.droplets).
    required: true
    choices: ["digitalocean.cloud.droplets"]
  token:
    description:
      - DigitalOcean API token.
      - There are several environment variables which can be used to provide this value.
      - C(DIGITALOCEAN_ACCESS_TOKEN), C(DIGITALOCEAN_TOKEN), C(DO_API_TOKEN), C(DO_API_KEY), C(DO_OAUTH_TOKEN) and C(OAUTH_TOKEN)
    type: str
    required: false
  client_override_options:
    description:
      - Client override options (developer use).
      - For example, can be used to override the DigitalOcean API endpoint for an internal test suite.
      - If provided, these options will knock out existing options.
    type: dict
    required: false
  attributes:
    description:
      - Droplet attributes to include as host variables.
      - Consult the API documentation U(https://docs.digitalocean.com/reference/api/api-reference/#operation/droplets_create) for attribute examples.
      - |
        Note: The C(tags) attribute will be automatically renamed to C(do_tags) to avoid
        conflicting with Ansible's reserved C(tags) variable used for task tagging.
    type: list
    elements: str
    required: false
"""


EXAMPLES = r"""
plugin: digitalocean.cloud.droplets
cache: true
cache_plugin: ansible.builtin.jsonfile
cache_connection: /tmp/digitalocean_droplets_inventory
cache_timeout: 300
#
#  By default, this plugin will consult the following environment variables for the API token:
#  DIGITALOCEAN_ACCESS_TOKEN, DIGITALOCEAN_TOKEN, DO_API_TOKEN, DO_API_KEY, DO_OAUTH_TOKEN, OAUTH_TOKEN
#
#  The API token can also be set statically (but please, avoid committing secrets):
#  token: hunter2
#
#  Or, lookup plugins can be used:
#  token: "{{ lookup('ansible.builtin.pipe', '/script/which/echoes/token.sh') }}"
#  token: "{{ lookup('ansible.builtin.env', 'MY_DO_TOKEN') }}"
#
attributes:
  - id
  - memory
  - vcpus
  - disk
  - locked
  - status
  - kernel
  - created_at
  - features
  - backup_ids
  - next_backup_window
  - snapshot_ids
  - image
  - volume_ids
  - size
  - size_slug
  - networks
  - region
  - tags  # Note: Will be available as 'do_tags' to avoid Ansible reserved name
  - vpc_uuid
compose:
  ansible_host: networks.v4 | selectattr("type", "eq", "public") | map(attribute="ip_address") | first
  class: size.description | lower
  distribution: image.distribution | lower
keyed_groups:
  - key: image.slug | default("null", true)
    prefix: image
    separator: "_"
  - key: do_tags  # Use 'do_tags' instead of 'tags' to avoid Ansible reserved variable name
    prefix: tag
    separator: "_"
  - key: region.slug
    prefix: region
    separator: "_"
  - key: status
    prefix: status
    separator: "_"
  - key: vpc_uuid
    prefix: vpc
groups:
  basic: "'basic' in class"
  ubuntu: "'ubuntu' in distribution"
"""


from ansible.plugins.inventory import BaseInventoryPlugin, Cacheable, Constructable
from ansible.module_utils.basic import env_fallback
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonInventory,
    DigitalOceanFunctions,
)


class InventoryModule(BaseInventoryPlugin, Cacheable, Constructable):
    NAME = "digitalocean.cloud.droplets"

    VALID_ENDSWITH = (
        "inventory.yml",
        "digitalocean.yml",
        "do.yml",
        "cloud.yml",
        "droplets.yml",
    )

    def verify_file(self, path):
        valid = False
        if super(InventoryModule, self).verify_file(path):
            if path.endswith(InventoryModule.VALID_ENDSWITH):
                valid = True
            else:
                self.display.v(
                    msg="Skipping due to inventory source file name mismatch "
                    + "the inventory file name must end with one of the following: "
                    + ", ".join(InventoryModule.VALID_ENDSWITH)
                )
        return valid

    def _get_droplets(self):
        cloud = DigitalOceanCommonInventory(self.config)
        droplets = DigitalOceanFunctions.get_paginated(
            module=None,
            obj=cloud.client.droplets,
            meth="list",
            key="droplets",
            params=None,
            exc=DigitalOceanCommonInventory.HttpResponseError,
        )
        return droplets

    def _populate(self):
        droplets = self._get_droplets()
        for droplet in droplets:
            host_name = droplet.get("name")
            if not host_name:
                continue
            self.inventory.add_host(host_name)

            for k, v in droplet.items():
                attributes = self.config.get("attributes", [])
                if k in attributes:
                    # Rename 'tags' to 'do_tags' to avoid Ansible reserved variable name
                    var_name = "do_tags" if k == "tags" else k
                    self.inventory.set_variable(host_name, var_name, v)

            host_vars = self.inventory.get_host(host_name).get_vars()

            self._set_composite_vars(
                self.get_option("compose"), host_vars, host_name, True
            )

            self._add_host_to_composed_groups(
                self.get_option("groups"), host_vars, host_name, True
            )

            self._add_host_to_keyed_groups(
                self.get_option("keyed_groups"),
                host_vars,
                host_name,
                True,
            )

    def parse(self, inventory, loader, path, cache=True):
        super(InventoryModule, self).parse(inventory, loader, path, cache)

        self.config = self._read_config_data(path)
        token = self.templar.template(self.config.get("token"))
        if not token:
            token = env_fallback(
                "DIGITALOCEAN_ACCESS_TOKEN",
                "DIGITALOCEAN_TOKEN",
                "DO_API_TOKEN",
                "DO_API_KEY",
                "DO_OAUTH_TOKEN",
                "OAUTH_TOKEN",
            )
        self.config.update({"token": token})

        cache_key = self.get_cache_key(path)
        use_cache = self.get_option("cache") and cache
        update_cache = self.get_option("cache") and not cache

        droplets = None
        if use_cache:
            try:
                droplets = self._cache[cache_key]
            except KeyError:
                update_cache = True

        if droplets is None:
            droplets = self._get_droplets()

        if update_cache:
            self._cache[cache_key] = droplets

        self._populate()
