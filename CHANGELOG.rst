=====================================
DigitalOcean Collection Release Notes
=====================================

.. contents:: Topics


v0.3.0
======

Minor Changes
-------------

- common - add C(client_override_options) and C(module_override_options) for experimental or future options (https://github.com/digitalocean/ansible-collection/pull/44).
- common - remove region validation from argument_specs to facilitate API test beds (https://github.com/digitalocean/ansible-collection/pull/44).
- droplet - add missing C(user_data) parameter (https://github.com/digitalocean/ansible-collection/pull/44).
- droplet_action_power - new module for changing power states on Droplets (https://github.com/digitalocean/ansible-collection/pull/44).
- droplet_action_resize - new module for resizing Droplets (https://github.com/digitalocean/ansible-collection/pull/44).
- droplet_action_snapshot - new module for taking Droplet snapshots (https://github.com/digitalocean/ansible-collection/pull/44).

Breaking Changes / Porting Guide
--------------------------------

- droplet_action - removed and will be split into individual actions (https://github.com/digitalocean/ansible-collection/pull/44).

Bugfixes
--------

- integration - do not ignore errors for C(billing_history_information) test (https://github.com/digitalocean/ansible-collection/issues/44).

New Modules
-----------

- droplet_action_power - Set power states of a Droplet
- droplet_action_resize - Resize a Droplet
- droplet_action_snapshot - Take a snapshot of a Droplet

v0.2.0
======

Release Summary
---------------

Add many more modules.

Minor Changes
-------------

- add many more modules (https://github.com/digitalocean/ansible-collection/pull/10).
- add more modules (https://github.com/digitalocean/ansible-collection/pull/10).
- configured ansible-lint to use the production profile (https://github.com/digitalocean/ansible-collection/pull/20).
- set up a devcontainer configuration allowing contributors to the project to use GitHub Codespaces or other tools that leverage devcontainer configurations (https://github.com/digitalocean/ansible-collection/pull/18).
- updated python dependencies (https://github.com/digitalocean/ansible-collection/pull/18).
- updated the pyproject.toml to more loosely define dependency versions, allowing the poetry lockfile to pin explicit versions (https://github.com/digitalocean/ansible-collection/pull/18).

Bugfixes
--------

- integration tests - fix missing C(PR_NUMBER) when run on C(main) (https://github.com/digitalocean/ansible-collection/pull/22).

New Modules
-----------

- balance_info - Retrieve the balances on a customer's account
- billing_history_info - Retrieve a list of all billing history entries
- cdn_endpoints - Manage CDN endpoints
- cdn_endpoints_info - List all of the CDN endpoints available on your account
- certificate - Manage certificates
- certificates_info - List all of the certificates available on your account
- database_cluster - Create or delete database clusters
- database_clusters_info - List all of the database clusters on your account
- domain - Manage domains
- domain_record - Manage domain records
- domain_records_info - Retrieve a listing of all of the domain records for a domain
- domains_info - Retrieve a list of all of the domains in your account
- droplet - Create or delete Droplets
- droplet_action - Perform Droplet actions
- droplets_info - List all Droplets in your account
- firewall - Create or delete firewalls
- firewalls_info - List all firewalls on your account
- images_info - List all of the images available on your account
- kubernetes_cluster - Create or delete Kubernetes clusters
- kubernetes_clusters_info - Retrieve a list of all of the Kubernetes clusters in your account
- load_balancer - Create or delete load balancers
- load_balancers_info - Retrieve a list of all of the load balancers in your account
- monitoring_alert_policies_info - Returns all alert policies that are configured for the given account
- monitoring_alert_policy - Create or delete monitoring alert policy
- one_clicks_info - List all available 1-Click applications
- project - Create or delete projects
- projects_info - Retrieve a list of all of the projects in your account
- regions_info - List all of the regions that are available
- reserved_ip - Create or delete reserved IPs
- reserved_ips_info - List all reserved IPs on your account
- sizes_info - List all of available Droplet sizes
- snapshot - Delete snapshots
- snapshots_info - Retrieve a list of all of the snapshots in your account
- ssh_key - Create or delete SSH keys
- ssh_keys_info - List all of the keys in your account
- tag - Create or delete tags
- tags_info - List all of the tags on your account
- volume - Create or delete volumes
- volume_action - Attach or detach volumes from Droplets
- volume_snapshot - Create or delete volume snapshots
- volumes_info - List all of the block storage volumes available on your account
- vpc - Create or delete VPCs
- vpcs_info - List all of the VPCs on your account

v0.1.2
======

Release Summary
---------------

Small Shark-a-Hack iterations.

Minor Changes
-------------

- small Shark-a-Hack iterations (https://github.com/digitalocean/ansible-collection/pull/9).

Bugfixes
--------

- common - ignore C(pydo) module unused (https://github.com/digitalocean/ansible-collection/pull/9).

v0.1.1
======

Release Summary
---------------

Just bumping the version.

Minor Changes
-------------

- just bumping the version (https://github.com/digitalocean/ansible-collection/pull/8).

v0.1.0
======

Release Summary
---------------

Initial release of the Collection.

Minor Changes
-------------

- add Galaxy publish workflow (https://github.com/digitalocean/ansible-collection/pull/7).

New Modules
-----------

- account_info - Show information about the current user account
