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
import jmespath
import logging
from botocore.exceptions import ClientError
from skew.resources.aws import AWSResource
from skew.awsclient import get_awsclient

LOG = logging.getLogger(__name__)


class CloudTrail(AWSResource):
    @classmethod
    def enumerate(cls, arn, region, account, resource_id=None, **kwargs):
        client = get_awsclient(cls.Meta.service, region, account, **kwargs)
        try:
            data = client.call("list_trails", query="Trails[]")
            if data:
                if account and account != "*":
                    data = filter(
                        lambda d: account == d["TrailARN"].split(":")[4], data
                    )
                if region and region != "*":
                    data = filter(lambda d: region == d["HomeRegion"], data)
                if resource_id and resource_id != "*":
                    data = filter(lambda d: cls.filter(arn, resource_id, d), data)
                return map(lambda d: cls(client, d, arn.query), data)
        except ClientError as e:
            LOG.debug(e)
            # if the error is because the resource was not found, be quiet
            if "NotFound" not in e.response["Error"]["Code"]:
                raise
        return []

    @classmethod
    def filter(cls, arn, resource_id, data):
        return resource_id == data["Name"]

    class Meta(object):
        service = "cloudtrail"
        type = "trail"

        filter_name = None
        detail_spec = ("get_trail", "Trail", "Name", "name")
        status_spec = ("get_trail_status", None, "Name", "name")
        id = "Name"
        name = "Name"
        tags_spec = (
            "list_tags",
            "ResourceTagList[].TagsList[]",
            "ResourceIdList[]",
            "name",
        )

        date = None
        dimension = None

    def __init__(self, client, data, query=None):
        super(CloudTrail, self).__init__(client, data, query)
        self._data = {
            **self._data,
            **self._feed_from_spec(attr_spec=self.Meta.detail_spec),
        }
        self._data["Status"] = self._feed_from_spec(attr_spec=self.Meta.status_spec)

    @property
    def arn(self):
        return self._data["TrailARN"]

    @property
    def tags(self):
        if self._tags is None:
            self._tags = {}
            self._data["Tags"] = self._client.call(
                "list_tags",
                query="ResourceTagList[].TagsList[]",
                ResourceIdList=[self.arn],
            )
            if "Tags" in self._data:
                self._tags = self._normalize_tags(self._data["Tags"])

        return self._tags