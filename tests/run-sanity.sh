#!/usr/bin/env bash
set -e

cd ~/.ansible/collections/ansible_collections/digitalocean/cloud
ansible-test sanity --python 3.11 --verbose "$@"
