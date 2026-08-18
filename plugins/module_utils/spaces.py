# -*- coding: utf-8 -*-
# Copyright: (c) 2023, Mark Mercado <mmercado@digitalocean.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


from traceback import format_exc

from ansible.module_utils.common.text.converters import to_native
from ansible_collections.digitalocean.cloud.plugins.module_utils.common import (
    DigitalOceanCommonModule,
)


class Spaces(DigitalOceanCommonModule):
    SPACES_TLD = "digitaloceanspaces.com"

    def __init__(self, module):
        super().__init__(module)
        self.name = module.params.get("name")
        self.region = module.params.get("region")
        self.aws_access_key_id = module.params.get("aws_access_key_id")
        self.aws_secret_access_key = module.params.get("aws_secret_access_key")
        self.boto_session = DigitalOceanCommonModule.boto3.session.Session()
        self.boto_client = self.boto_session.client(
            "s3",
            region_name=self.region,
            endpoint_url=f"https://{self.region}.{Spaces.SPACES_TLD}",
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

    def get(self):
        try:
            boto_response = self.boto_client.list_buckets()
        except Exception as e:
            self.module.fail_json(msg=to_native(e), exception=format_exc())

        boto_response_metadata = boto_response.get("ResponseMetadata")
        boto_http_status_code = boto_response_metadata.get("HTTPStatusCode")

        if boto_http_status_code == 200:
            spaces = [
                {
                    "name": space["Name"],
                    "region": self.region,
                    "endpoint_url": f"https://{self.region}.{Spaces.SPACES_TLD}",
                    "space_url": f"https://{space['Name']}.{self.region}.{Spaces.SPACES_TLD}",
                }
                for space in boto_response["Buckets"]
            ]

            if spaces:
                if self.name:  # Filter by single space name
                    spaces = [space for space in spaces if space["name"] == self.name]
                return spaces
            return []

        self.module.fail_json(
            changed=False,
            msg=f"Failed to list Spaces in {self.region}",
            error=boto_response_metadata,
        )

    def create(self):
        try:
            boto_response = self.boto_client.create_bucket(Bucket=self.name)
        except Exception as e:
            self.module.fail_json(msg=to_native(e), exception=format_exc())

        boto_response_metadata = boto_response.get("ResponseMetadata")
        boto_http_status_code = boto_response_metadata.get("HTTPStatusCode")

        if boto_http_status_code == 200:
            spaces = [
                {
                    "name": self.name,
                    "region": self.region,
                    "endpoint_url": f"https://{self.region}.{Spaces.SPACES_TLD}",
                    "space_url": f"https://{self.name}.{self.region}.{Spaces.SPACES_TLD}",
                }
            ]
            return spaces

        self.module.fail_json(
            changed=False,
            msg=f"Failed to create Space {self.name} in {self.region}",
            error=boto_response_metadata,
        )

    def delete(self):
        try:
            boto_response = self.boto_client.delete_bucket(Bucket=self.name)
        except Exception as e:
            self.module.fail_json(msg=to_native(e), exception=format_exc())

        boto_response_metadata = boto_response.get("ResponseMetadata")
        boto_http_status_code = boto_response_metadata.get("HTTPStatusCode")

        if boto_http_status_code == 204:
            return

        self.module.fail_json(
            changed=False,
            msg=f"Failed to delete Space {self.name} in {self.region}",
            error=boto_response_metadata,
        )
