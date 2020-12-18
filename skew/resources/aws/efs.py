# Copyright (c) 2014 Scopely, Inc.
# Copyright (c) 2015 Mitch Garnaat
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import logging

import jmespath

from skew.resources.aws import AWSResource
from skew.awsclient import get_awsclient


LOG = logging.getLogger(__name__)


class Filesystem(AWSResource):
    class Meta(object):
        service = "efs"
        type = "filesystem"
        enum_spec = ("describe_file_systems", "FileSystems", None)
        detail_spec = None
        id = "FileSystemId"
        tags_spec = ("describe_tags", "Tags[]", "FileSystemId", "id")
        filter_name = None
        name = "Name"
        date = "CreationTime"
        dimension = None

    @property
    def arn(self):
        # arn:aws:elasticfilesystem:us-east-1:123456789012:file-system-id/fs12345678
        return "arn:aws:%s:%s:%s:%s/%s" % (
            "elasticfilesystem",
            self._client.region_name,
            self._client.account_id,
            "file-system-id",
            self.id,
        )

    def __init__(self, client, data, query=None):
        super(Filesystem, self).__init__(client, data, query)
        # Asset name is get by tags if defined, or is FileSystemId
        self._name = self.tags.get("Name", self.data["FileSystemId"])

    def sleek(self):
        self._data["SizeInBytes"] = 0

    @classmethod
    def set_tags(cls, arn, region, account, tags, resource_id=None, **kwargs):
        client = get_awsclient(cls.Meta.service, region, account, **kwargs)
        tags_list = [dict(Key=k, Value=str(v)) for k, v in tags.items()]
        x = client.call("create_tags", FileSystemId=arn.split("/")[-1], Tags=tags_list)
        return x

    @classmethod
    def unset_tags(cls, arn, region, account, tag_keys, resource_id=None, **kwargs):
        client = get_awsclient(cls.Meta.service, region, account, **kwargs)
        x = client.call(
            "delete_tags", FileSystemId=arn.split("/")[-1], TagKeys=tag_keys
        )
        return x
