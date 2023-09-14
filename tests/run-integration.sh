#!/bin/bash -e

cd ~/.ansible/collections/ansible_collections/digitalocean/cloud
ansible-test integration
