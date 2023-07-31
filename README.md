# DigitalOcean Collection

<p align="left" width="100%">
<img src="do+a.png"
     alt="DigitalOcean + Ansible"
     title="DigitalOcean + Ansible"
     height=300>
</p>

> **Warning**
> This collection is not ready for use!

This repository contains the `digitalocean.cloud` Ansible Collection.

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/digitalocean/ansible-collection?quickstart=1)

## DigitalOcean Collection for Ansible

[![Integration tests](https://github.com/digitalocean/ansible-collection/actions/workflows/ansible-test-integration.yml/badge.svg)](https://github.com/digitalocean/ansible-collection/actions/workflows/ansible-test-integration.yml)
[![Lint extra docsite docs and links](https://github.com/digitalocean/ansible-collection/actions/workflows/extra-docs-linting.yml/badge.svg)](https://github.com/digitalocean/ansible-collection/actions/workflows/extra-docs-linting.yml)
[![Publish Collection on Galaxy](https://github.com/digitalocean/ansible-collection/actions/workflows/publish-galaxy.yml/badge.svg)](https://github.com/digitalocean/ansible-collection/actions/workflows/publish-galaxy.yml)
[![Pull request integration tests](https://github.com/digitalocean/ansible-collection/actions/workflows/pull-request-integration.yml/badge.svg)](https://github.com/digitalocean/ansible-collection/actions/workflows/pull-request-integration.yml)
[![Python psf/black](https://github.com/digitalocean/ansible-collection/actions/workflows/psf-black.yml/badge.svg)](https://github.com/digitalocean/ansible-collection/actions/workflows/psf-black.yml)
[![Sanity tests](https://github.com/digitalocean/ansible-collection/actions/workflows/ansible-test-sanity.yml/badge.svg)](https://github.com/digitalocean/ansible-collection/actions/workflows/ansible-test-sanity.yml)
[![Unit tests](https://github.com/digitalocean/ansible-collection/actions/workflows/ansible-test-unit.yml/badge.svg)](https://github.com/digitalocean/ansible-collection/actions/workflows/ansible-test-unit.yml)

This collection can be used to manage infrastructure in the [DigitalOcean](https://www.digitalocean.com/) cloud.
The API documentation is located [here](https://docs.digitalocean.com/reference/api/api-reference/).

## Code of Conduct

We follow the [Ansible Code of Conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html) in all our interactions within this project.

If you encounter abusive behavior, please refer to the [policy violations](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html#policy-violations) section of the Code for information on how to raise a complaint.

## Communication

Join us in [Libera.chat](https://libera.chat/) in the `#ansible-digitalocean` for collection development questions or DigitalOcean Community Discord in the [`#ansible`](https://discord.com/channels/707751027973161132/1069237079642476604) channel.

## Contributing to this collection

<!--Describe how the community can contribute to your collection. At a minimum, fill up and include the CONTRIBUTING.md file containing how and where users can create issues to report problems or request features for this collection. List contribution requirements, including preferred workflows and necessary testing, so you can benefit from community PRs. If you are following general Ansible contributor guidelines, you can link to - [Ansible Community Guide](https://docs.ansible.com/ansible/devel/community/index.html). List the current maintainers (contributors with write or higher access to the repository). The following can be included:-->

The content of this collection is made by people like you, a community of individuals collaborating on making the world better through developing automation software.

We are actively accepting new contributors.

Any kind of contribution is very welcome.

You don't know how to start? Refer to our [contribution guide](CONTRIBUTING.md)!

We use the following guidelines:

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [REVIEW_CHECKLIST.md](REVIEW_CHECKLIST.md)
- [Ansible Community Guide](https://docs.ansible.com/ansible/latest/community/index.html)
- [Ansible Development Guide](https://docs.ansible.com/ansible/devel/dev_guide/index.html)
- [Ansible Collection Development Guide](https://docs.ansible.com/ansible/devel/dev_guide/developing_collections.html#contributing-to-collections)

## Collection maintenance

The current maintainers are listed in the [MAINTAINERS](MAINTAINERS) file.
If you have questions or need help, feel free to mention them in the proposals.

To learn how to maintain / become a maintainer of this collection, refer to the [Maintainer guidelines](MAINTAINING.md).

## Governance

The process of decision making in this collection is based on discussing and finding consensus among participants.

Every voice is important. If you have something on your mind, create an issue or dedicated discussion and let's discuss it!

## Tested with versions

| Ansible       | Python |
| ------------- | ------ |
| `stable-2.13` | `3.9`  |
| `stable-2.14` | `3.9`  |
| `stable-2.15` | `3.10` |
| `devel`       | `3.10` |

## External requirements

```text
azure-core==1.26.1
pydo==0.1.4
```

The following should install the requirements for your account:

```shell
pip3 install --user azure-core==1.26.1 pydo==0.1.4
```

There is a [pyproject.toml](./pyproject.toml) is the root of this repository as well if you use [Poetry](https://python-poetry.org/) or similar.

## Included content

| Module                            | Description                                     |
| --------------------------------- | ----------------------------------------------- |
| `digitalocean.cloud.account_info` | Show information about the current user account |

## Using this collection

There are sample playbooks in the [playbooks](./playbooks) directory.
Be sure to set the `DIGITALOCEAN_TOKEN` environment variable as most modules require authentication.

[This](./playbooks/account_info.yml) is a sample playbook which returns your DigitalOcean account information:

```yaml
---
- name: Account info
  hosts: localhost
  connection: local
  gather_facts: false
  tasks:
    - name: Get account information
      digitalocean.cloud.account_info:
```

Output should look similar to the following:

```shell
❯ ANSIBLE_STDOUT_CALLBACK=yaml ansible-playbook -i localhost, -c local playbooks/account_info.yml -v
Using /Users/mmercado/.ansible.cfg as config file

PLAY [Account info] **********************************************************************************************

TASK [Get account information] ***********************************************************************************
ok: [localhost] => changed=false
  account:
    droplet_limit: 25
    email: mmercado@digitalocean.com
    email_verified: true
    floating_ip_limit: 3
    name: Mark Mercado
    reserved_ip_limit: 3
    status: active
    status_message: ''
    team:
      name: FOSS
      uuid: 3281ad4a-0092-4e6b-abd2-c7a7ed111503
    uuid: eab13a8a-99e3-4ffd-a587-b8a7789f0090
    volume_limit: 100
  msg: Current account information

PLAY RECAP *******************************************************************************************************
localhost                  : ok=1    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
```

### Installing the Collection from Ansible Galaxy

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:

```shell
ansible-galaxy collection install digitalocean.cloud
```

You can also include it in a `requirements.yml` file and install it with `ansible-galaxy collection install -r requirements.yml`, using the format:

```yaml
---
collections:
  - name: digitalocean.cloud
```

Note that if you install the collection from Ansible Galaxy, it will not be upgraded automatically when you upgrade the `ansible` package.
To upgrade the collection to the latest available version, run the following command:

```shell
ansible-galaxy collection install digitalocean.cloud --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository).
Use the following syntax to install version `0.1.1`:

```shell
ansible-galaxy collection install digitalocean.cloud:==0.1.1
```

See [Ansible Using collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

## Release notes

See the [changelog](https://github.com/digitalocean/ansible-collection/tree/main/CHANGELOG.rst).

## Roadmap

<!-- Optional. Include the roadmap for this collection, and the proposed release/versioning strategy so users can anticipate the upgrade/update cycle. -->

TBD

## More information

- [Ansible Collection overview](https://github.com/ansible-collections/overview)
- [Ansible User guide](https://docs.ansible.com/ansible/devel/user_guide/index.html)
- [Ansible Developer guide](https://docs.ansible.com/ansible/devel/dev_guide/index.html)
- [Ansible Collections Checklist](https://github.com/ansible-collections/overview/blob/main/collection_requirements.rst)
- [Ansible Community code of conduct](https://docs.ansible.com/ansible/devel/community/code_of_conduct.html)
- [The Bullhorn (the Ansible Contributor newsletter)](https://us19.campaign-archive.com/home/?u=56d874e027110e35dea0e03c1&id=d6635f5420)
- [News for Maintainers](https://github.com/ansible-collections/news-for-maintainers)

## Licensing

GNU General Public License v3.0 or later.

See [LICENSE](https://www.gnu.org/licenses/gpl-3.0.txt) to see the full text.
