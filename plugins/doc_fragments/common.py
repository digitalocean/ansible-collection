# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment(object):
    DOCUMENTATION = r"""
options:
  state:
    description:
      - State of the resource, C(present) to create, C(absent) to destroy.
    type: str
    choices: [ present, absent ]
    default: present
  timeout:
    description:
      - Polling timeout in seconds.
    type: int
    default: 300
  token:
    description:
      - DigitalOcean API token.
      - There are several environment variables which can be used to provide this value.
      - C(DIGITALOCEAN_ACCESS_TOKEN), C(DIGITALOCEAN_TOKEN), C(DO_API_TOKEN), C(DO_API_KEY), C(DO_OAUTH_TOKEN) and C(OAUTH_TOKEN)
    type: str
    aliases: [ oauth_token, api_token ]
    required: false
  client_override_options:
    description:
      - Client override options (developer use).
      - For example, can be used to override the DigitalOcean API endpoint for an internal test suite.
      - If provided, these options will knock out existing options.
    type: dict
    required: false
  module_override_options:
    description:
      - Module override options (developer use).
      - Can be used to override module options to support experimental or future options.
      - If provided, these options will knock out existing options.
    type: dict
    required: false
"""
