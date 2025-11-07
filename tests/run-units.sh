#!/usr/bin/env bash
set -e

cd ~/.ansible/collections/ansible_collections/digitalocean/cloud
ansible-test units --python 3.11 --verbose "$@"
