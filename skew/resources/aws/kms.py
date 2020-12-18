# Copyright (c) 2020 Jerome Guibert
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

from botocore.exceptions import ClientError
from skew.resources.aws import AWSResource
from skew.awsclient import get_awsclient


LOG = logging.getLogger(__name__)


class Key(AWSResource):
    class Meta(object):
        service = "kms"
        type = "key"

        enum_spec = ("list_keys", "Keys[]", None)
        filter_name = None
        id = "KeyId"

        attr_spec = {
            "describe": ("describe_key", "KeyMetadata", "KeyId", "id"),
            "key_policy": ("get_key_policy", "Policy", "KeyId", "id"),
            "key_rotation_status": (
                "get_key_rotation_status",
                "KeyRotationEnabled",
                "KeyId",
                "id",
            ),
            "aliases": ("list_aliases", "Aliases[]", "KeyId", "id"),
        }

        tags_spec = ("list_resource_tags", "Tags[]", "KeyId", "arn")

    @classmethod
    def filter(cls, arn, resource_id, data):
        return resource_id == data["KeyId"]

    def __init__(self, client, data, query=None):
        super(Key, self).__init__(client, data, query)
        self._data["KeyMetadata"] = self._feed_from_spec(
            attr_spec=self.Meta.attr_spec["describe"]
        )
        self._data["Policy"] = self._feed_from_spec(
            attr_spec=self.Meta.attr_spec["key_policy"]
        )
        self._data["KeyRotationEnabled"] = self._feed_from_spec(
            attr_spec=self.Meta.attr_spec["key_rotation_status"]
        )
        self._data["Aliases"] = self._feed_from_spec(
            attr_spec=self.Meta.attr_spec["aliases"]
        )
