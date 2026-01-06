=====================================
DigitalOcean Collection Release Notes
=====================================

.. contents:: Topics

v1.9.0
======

Minor Changes
-------------

- actions_info - new module to list account actions history.
- app - new module to manage App Platform applications.
- apps_info - new module to list App Platform applications.
- byoip_prefix - new module to manage BYOIP prefixes.
- byoip_prefixes_info - new module to list BYOIP prefixes.
- container_registry - new module to manage container registries.
- database_backups_info - new module to list database cluster backups.
- database_config - new module to configure database cluster settings.
- database_config_info - new module to get database cluster configuration.
- database_connection_pool - new module to manage database connection pools.
- database_connection_pools_info - new module to list database connection pools.
- database_db - new module to manage databases within a cluster.
- database_dbs_info - new module to list databases in a cluster.
- database_firewall - new module to manage database firewall rules.
- database_firewall_rules_info - new module to list database firewall rules.
- database_maintenance_window - new module to configure database maintenance windows.
- database_replica - new module to manage database read replicas.
- database_replicas_info - new module to list database replicas.
- database_user - new module to manage database users.
- database_users_info - new module to list database users.
- droplet_autoscale_pool - new module to manage Droplet autoscale pools.
- droplet_autoscale_pools_info - new module to list Droplet autoscale pools.
- droplet_backups_info - new module to list Droplet backups.
- droplet_kernels_info - new module to list available Droplet kernels.
- droplet_neighbors_info - new module to list Droplet neighbors.
- droplet_snapshots_info - new module to list Droplet snapshots.
- floating_ip - new module to manage floating IPs (legacy compatibility).
- floating_ip_action - new module to assign/unassign floating IPs (legacy compatibility).
- floating_ips_info - new module to list floating IPs (legacy compatibility).
- function_namespace - new module to manage Functions namespaces.
- function_namespaces_info - new module to list Functions namespaces.
- image - new module to manage custom images.
- image_action - new module to perform image actions (transfer, convert).
- invoice_items_info - new module to get invoice line items.
- invoices_info - new module to list account invoices.
- kubernetes_node_pool - new module to manage Kubernetes node pools.
- kubernetes_node_pools_info - new module to list Kubernetes node pools.
- nfs - new module to manage NFS file systems.
- nfs_action - new module to perform NFS actions (resize).
- nfs_info - new module to list NFS file systems.
- project_resource - new module to assign resources to projects.
- reserved_ipv6 - new module to manage reserved IPv6 addresses.
- reserved_ipv6_action - new module to assign/unassign reserved IPv6.
- reserved_ipv6s_info - new module to list reserved IPv6 addresses.
- spaces_key - new module to manage Spaces access keys.
- spaces_keys_info - new module to list Spaces access keys.
- uptime_alert - new module to manage uptime check alerts.
- uptime_alerts_info - new module to list uptime check alerts.
- vpc_nat_gateway - new module to manage VPC NAT gateways.
- vpc_nat_gateways_info - new module to list VPC NAT gateways.
- vpc_peering - new module to manage VPC peerings.
- vpc_peerings_info - new module to list VPC peerings.

Bugfixes
--------

- tests - update pydo version from 0.1.7 to 0.23.0 in test requirements to fix CI failures for modules using newer PyDO API attributes.

New Modules
-----------

- actions_info - List all actions that have been executed on your account
- app - Create or delete App Platform applications
- apps_info - List all App Platform applications on your account
- byoip_prefix - Manage Bring Your Own IP (BYOIP) prefixes
- byoip_prefixes_info - List all BYOIP prefixes on your account
- container_registry - Create or delete container registry
- database_backups_info - List all backups for a database cluster
- database_config - Configure database cluster settings
- database_config_info - Get database cluster configuration
- database_connection_pool - Create or delete database connection pools
- database_connection_pools_info - List all connection pools for a database cluster
- database_db - Create or delete databases within a cluster
- database_dbs_info - List all databases within a cluster
- database_firewall - Manage database cluster firewall rules
- database_firewall_rules_info - List database cluster firewall rules
- database_maintenance_window - Configure database cluster maintenance window
- database_replica - Create or delete database read-only replicas
- database_replicas_info - List all read-only replicas for a database cluster
- database_user - Create or delete database users
- database_users_info - List all database users in a cluster
- droplet_autoscale_pool - Create or delete Droplet Autoscale Pools
- droplet_autoscale_pools_info - List all Droplet Autoscale Pools on your account
- droplet_backups_info - List backups for a Droplet
- droplet_kernels_info - List available kernels for a Droplet
- droplet_neighbors_info - List Droplet neighbors
- droplet_snapshots_info - List snapshots for a Droplet
- floating_ip - Create or delete floating IPs (legacy)
- floating_ip_action - Assign or unassign a floating IP to a Droplet (legacy)
- floating_ips_info - List all floating IPs on your account (legacy)
- function_namespace - Create or delete Functions namespaces
- function_namespaces_info - List all Functions namespaces on your account
- image - Manage custom images
- image_action - Perform actions on images
- invoice_items_info - Get invoice items by UUID
- invoices_info - List account invoices
- kubernetes_node_pool - Create, update, or delete Kubernetes node pools
- kubernetes_node_pools_info - List all node pools in a Kubernetes cluster
- nfs - Create or delete NFS file shares
- nfs_action - Perform actions on NFS file shares
- nfs_info - List all NFS file shares on your account
- project_resource - Assign or remove resources from a project
- reserved_ipv6 - Create or delete reserved IPv6 addresses
- reserved_ipv6_action - Assign or unassign a reserved IPv6 address to a Droplet
- reserved_ipv6s_info - List all reserved IPv6 addresses on your account
- spaces_key - Create or delete Spaces access keys
- spaces_keys_info - List all Spaces access keys on your account
- uptime_alert - Create or delete uptime check alerts
- uptime_alerts_info - List all alerts for an uptime check
- vpc_nat_gateway - Create or delete VPC NAT Gateways
- vpc_nat_gateways_info - List all VPC NAT Gateways on your account
- vpc_peering - Create or delete VPC Peerings
- vpc_peerings_info - List all VPC Peerings on your account

v1.8.0
======

Minor Changes
-------------

- project_resources - add new module project_resources to assign resources to a project by project name or ID (https://github.com/digitalocean/ansible-collection/issues/119).

New Modules
-----------

- project_resources - Assign resources to a project

v1.7.0
======

Minor Changes
-------------

- droplets inventory plugin - add two-tier filtering system with api_filters for server-side filtering (tag_name, name) and filters for client-side Jinja2 template filtering. This addresses performance issues for large infrastructures by reducing API response size and provides granular control for environment isolation.

v1.6.0
======

Minor Changes
-------------

- Bump dependency versions via Dependabot (https://github.com/digitalocean/ansible-collection/pull/260).

Bugfixes
--------

- monitoring_alert_policy - Fixed idempotency by re-enabling description comparison (https://github.com/digitalocean/ansible-collection/issues/265).
- monitoring_alert_policy - Fixed typo 'desciption' to 'description' in API request body (https://github.com/digitalocean/ansible-collection/issues/264).

v1.5.0
======

Breaking Changes / Porting Guide
--------------------------------

- droplets inventory plugin - the C(tags) attribute is now automatically renamed to C(do_tags) when included in the C(attributes) list to avoid conflicting with Ansible's reserved C(tags) variable. Users should update their inventory configurations to use C(do_tags) in C(keyed_groups), C(compose), and C(groups) sections (https://github.com/digitalocean/ansible-collection/issues/249).

Bugfixes
--------

- droplet_action_resize - fixed to properly capture and poll the action response from the API instead of repeatedly querying the droplet state. The action response is now returned in the module output and used to determine when the resize operation completes (https://github.com/digitalocean/ansible-collection/issues/243).
- droplets inventory plugin - fixed warning "[WARNING]: Found variable using reserved name 'tags'" by automatically renaming the C(tags) attribute to C(do_tags) to avoid conflicting with Ansible's reserved variable name (https://github.com/digitalocean/ansible-collection/issues/249).
- ssh_key - module now handles the case where an SSH key with the same public key already exists on the account, making it idempotent instead of failing with a 422 error (https://github.com/digitalocean/ansible-collection/issues/102).
- tag - fixed KeyError when tag creation fails due to validation errors. The module now properly catches and reports API error messages instead of showing a cryptic KeyError (https://github.com/digitalocean/ansible-collection/issues/181).

v1.4.0
======

Minor Changes
-------------

- common, droplet_action_power, droplet_action_resize, droplet_action_snapshot - standardized error messages to include droplet IDs when multiple droplets with the same name are found, improving debugging experience. Added comprehensive unit tests for droplet_action modules (https://github.com/digitalocean/ansible-collection/issues/250).

Bugfixes
--------

- droplet - fix C(unique_name) parameter not working correctly due to API name parameter not being supported. The module now fetches all droplets and filters client-side to properly detect existing droplets and prevent duplicate creation (https://github.com/digitalocean/ansible-collection/issues/250).

v1.3.0
======

Minor Changes
-------------

- dependencies - bump aiohttp from 3.9.5 to 3.10.2 (https://github.com/digitalocean/ansible-collection/issues/233).
- dependencies - bump certifi from 2024.6.2 to 2024.7.4 (https://github.com/digitalocean/ansible-collection/issues/233).
- dependencies - bump cryptography from 42.0.8 to 43.0.1 (https://github.com/digitalocean/ansible-collection/issues/233).
- reserved_ip_assign - new module for assigning an existing reserved IP to a Droplet (https://github.com/digitalocean/ansible-collection/issues/233).

New Modules
-----------

- reserved_ip_assign - Create and/or assign a reserved IP to a Droplet

v1.2.1
======

Minor Changes
-------------

- droplet - Add more Droplet tests and fix Droplet "noop" resize (https://github.com/digitalocean/ansible-collection/issues/245).

v1.2.0
======

Major Changes
-------------

- database_cluster -  Replace Redis with Valkey (https://github.com/digitalocean/ansible-collection/issues/241).

Bugfixes
--------

- droplet - Fix resize for new Droplets (https://github.com/digitalocean/ansible-collection/issues/239).

v1.1.0
======

Minor Changes
-------------

- droplet - Add ``resize`` and ``resize_disk`` functionality (https://github.com/digitalocean/ansible-collection/issues/236).

v1.0.0
======

Release Summary
---------------

Bump Python, project-wide, to 3.11.11. Fix ``state: absent`` bug in the Droplet module. Disable integration testing for the ``monitoring_alert_policy`` and ``one_click`` modules since they are broken (https://github.com/digitalocean/ansible-collection/pull/234).

Minor Changes
-------------

- Bump Python to 3.11.11 and Poetry to 1.8.5 (https://github.com/digitalocean/ansible-collection/issues/229).
- monitoring_alert_policy - mark integration test as ``disabled`` since it is broken (https://github.com/digitalocean/ansible-collection/issues/229)."
- one_click - mark this integration test as ``disabled`` since it is broken (https://github.com/digitalocean/ansible-collection/issues/229)."

Bugfixes
--------

- droplet - add misisng ``droplet_id`` parameter when for ``state: absent`` (https://github.com/digitalocean/ansible-collection/issues/229).

v0.6.0
======

Minor Changes
-------------

- added an action group 'digitalocean.cloud.all' for use with module defaults: https://docs.ansible.com/ansible/latest/user_guide/playbooks_module_defaults.html (https://github.com/digitalocean/ansible-collection/pull/180)

v0.5.1
======

Minor Changes
-------------

- Bump Kubernetes version in its integration test (https://github.com/digitalocean/ansible-collection/issues/100).
- Fix broken links due to Ansible Galaxy NG launch (https://github.com/digitalocean/ansible-collection/pull/91).
- Lint tweaked ansible-lint configuration so production profile is now the target for this repo (https://github.com/digitalocean/ansible-collection/pull/104).

v0.5.0
======

Minor Changes
-------------

- ci - configure dependabot for grouped dependency updates (https://github.com/digitalocean/ansible-collection/pull/84).

New Modules
-----------

- container_registry_info - Get information about your container registry
- one_click - Install Kubernetes 1-Click applications
- project_resources_info - Retrieve a list of all of the project resources in your account
- space - Manage Spaces
- spaces_info - List all of the Spaces in your account
- uptime_check - Create or delete Uptime checks
- uptime_checks_info - List all of the Uptime checks on your account
- uptime_checks_state_info - Get the state of an Uptime check

v0.4.0
======

Bugfixes
--------

- database_cluster - fix C(database_cluster) module and reenable integration test (https://github.com/digitalocean/ansible-collection/pull/60).
- kubernetes_cluster - fix C(kubernetes_cluster) module polling and refactor integration test (https://github.com/digitalocean/ansible-collection/issues/62).
- project - fix C(project) module with API workaround and add integration test (https://github.com/digitalocean/ansible-collection/pull/61).

New Plugins
-----------

Inventory
~~~~~~~~~

- droplets - Droplets dynamic inventory plugin

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
