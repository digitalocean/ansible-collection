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
  api_filters:
    description:
      - Server-side API filters to limit droplets fetched from the DigitalOcean API.
      - Reduces API response size and improves performance for large infrastructures.
      - Applied before droplets are retrieved, minimizing network transfer and processing time.
    type: dict
    required: false
    suboptions:
      tag_name:
        description:
          - Filter droplets by tag name.
          - Only droplets with this exact tag will be returned.
        type: str
        required: false
      name:
        description:
          - Filter droplets by name.
          - Matches droplets with this exact name.
        type: str
        required: false
  filters:
    description:
      - Client-side filters using Jinja2 templates.
      - Applied after droplets are retrieved from the API.
      - All filter expressions must evaluate to true for a host to be included.
      - Use this for complex filtering logic not supported by API filters (e.g., region filtering).
    type: list
    elements: str
    required: false
    default: []
"""


EXAMPLES = r"""
# Basic example with caching
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

# Example with API-level filtering (server-side)
# This reduces API response size and improves performance
# plugin: digitalocean.cloud.droplets
# api_filters:
#   tag_name: staging  # Only fetch droplets with 'staging' tag
# attributes:
#   - region
#   - tags
#   - status

# Example with client-side filtering (Jinja2 templates)
# Applied after droplets are retrieved from the API
# plugin: digitalocean.cloud.droplets
# attributes:
#   - region
#   - tags
#   - status
# filters:
#   - 'region.slug == "ams3"'  # Only include droplets in AMS3 region
#   - 'status == "active"'      # Only include active droplets

# Example with two-tier filtering (API + client-side)
# Most efficient: API filter reduces network load, client filter adds precision
# plugin: digitalocean.cloud.droplets
# api_filters:
#   tag_name: staging  # API filter: only fetch staging droplets
# attributes:
#   - region
#   - tags
#   - status
#   - networks
# filters:
#   - 'region.slug == "ams3"'  # Client filter: only AMS3 region
#   - '"staging" in do_tags'    # Client filter: verify staging tag
# compose:
#   ansible_host: networks.v4 | selectattr("type", "eq", "public") | map(attribute="ip_address") | first
# keyed_groups:
#   - key: region.slug
#     prefix: region
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

    def _passes_filters(self, filters, variables, host, strict=False):
        """Apply client-side Jinja2 template filters to a host.

        Args:
            filters: List of Jinja2 template strings to evaluate
            variables: Host variables to use in template evaluation
            host: Hostname being evaluated
            strict: Whether to raise errors on template evaluation failures

        Returns:
            bool: True if all filters pass, False otherwise
        """
        if not filters:
            return True

        if not isinstance(filters, list):
            filters = [filters]

        for template in filters:
            try:
                if not self._compose(template, variables):
                    self.display.vvv(f"Host {host} excluded by filter: {template}")
                    return False
            except Exception as e:
                if strict:
                    raise
                self.display.vvv(
                    f"Host {host} excluded due to filter error: {template} ({e})"
                )
                return False

        return True

    def _get_droplets(self):
        cloud = DigitalOceanCommonInventory(self.config)

        # Build API filter kwargs from api_filters option
        api_filters = self.get_option("api_filters") or {}
        filter_kwargs = {}
        if api_filters.get("tag_name"):
            filter_kwargs["tag_name"] = api_filters["tag_name"]
        if api_filters.get("name"):
            filter_kwargs["name"] = api_filters["name"]

        droplets = DigitalOceanFunctions.get_paginated(
            module=None,
            obj=cloud.client.droplets,
            meth="list",
            key="droplets",
            params=None,
            exc=DigitalOceanCommonInventory.HttpResponseError,
            **filter_kwargs,
        )
        return droplets

    def _populate(self, droplets):
        """Populate the inventory with the provided droplets.

        Args:
            droplets: List of droplet dictionaries fetched from the API.
                      This method now receives droplets as a parameter instead of
                      fetching them internally, eliminating redundant API calls and
                      ensuring cached droplets are properly used.
        """
        strict = self.get_option("strict")
        filters = self.get_option("filters")

        for droplet in droplets:
            host_name = droplet.get("name")
            if not host_name:
                continue

            # Build unwrapped vars dict for filter evaluation
            filter_vars = {}
            for k, v in droplet.items():
                attributes = self.config.get("attributes", [])
                if k in attributes:
                    # Rename 'tags' to 'do_tags' to avoid Ansible reserved variable name
                    var_name = "do_tags" if k == "tags" else k
                    filter_vars[var_name] = v

            # Apply client-side filters BEFORE adding to inventory
            if not self._passes_filters(filters, filter_vars, host_name, strict):
                self.display.vvv(f"Host {host_name} excluded by filters")
                continue

            # Add host and set variables (only for hosts that passed filters)
            self.inventory.add_host(host_name)
            for k, v in droplet.items():
                attributes = self.config.get("attributes", [])
                if k in attributes:
                    var_name = "do_tags" if k == "tags" else k
                    self.inventory.set_variable(host_name, var_name, v)

            host_vars = self.inventory.get_host(host_name).get_vars()

            self._set_composite_vars(
                self.get_option("compose"), host_vars, host_name, strict
            )

            self._add_host_to_composed_groups(
                self.get_option("groups"), host_vars, host_name, strict
            )

            self._add_host_to_keyed_groups(
                self.get_option("keyed_groups"),
                host_vars,
                host_name,
                strict,
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

        # Pass droplets to _populate instead of having it fetch them again.
        # This avoids redundant API calls and ensures cached data is used properly.
        self._populate(droplets)
