# Copyright (c) 2014 Scopely, Inc.
# Copyright (c) 2015 Mitch Garnaat
# Copyright (c) 2019 Christophe Morio
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

from skew.resources.aws import AWSResource
from skew.awsclient import get_awsclient


LOG = logging.getLogger(__name__)


class Stack(AWSResource):
    class Meta(object):
        service = "opsworks"
        type = "stack"
        enum_spec = ("describe_stacks", "Stacks", None)
        detail_spec = None
        id = "StackId"
        filter_name = None
        name = "Name"
        date = "CreatedAt"
        dimension = None
        tags_spec = ("list_tags", "Tags", "ResourceArn", "arn")

    @property
    def arn(self):
        return self._data.get("Arn")

    @classmethod
    def set_tags(cls, arn, region, account, tags, resource_id=None, **kwargs):
        # ResourceGroupsTaggingAPI supports regional stacks, but not classic (us-east-1)
        # opsworks.tag_resource() supports both
        client = get_awsclient(cls.Meta.service, region, account, **kwargs)
        r = client.call("tag_resource", ResourceArn=arn, Tags=tags)
        LOG.debug("Tag ARN %s, r=%s", arn, r)

    @classmethod
    def unset_tags(cls, arn, region, account, tag_keys, resource_id=None, **kwargs):
        # ResourceGroupsTaggingAPI supports regional stacks, but not classic (us-east-1)
        # opsworks.untag_resource() supports both
        client = get_awsclient(cls.Meta.service, region, account, **kwargs)
        r = client.call("untag_resource", ResourceArn=arn, TagKeys=tag_keys)
        LOG.debug("UnTag ARN %s, r=%s", arn, r)
