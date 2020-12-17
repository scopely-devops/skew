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


class Registery(AWSResource):
    @classmethod
    def enumerate(cls, arn, region, account, resource_id=None, **kwargs):
        client = get_awsclient(cls.Meta.service, region, account, **kwargs)
        try:
            data = client.call("describe_registry")
            if data:
                if "ResponseMetadata" in data:
                    del data["ResponseMetadata"]
                data[
                    "RegisteryUri"
                ] = f"{data['registryId']}.dkr.ecr.{region}.amazonaws.com"

                return [Registery(client, data, arn.query)]
        except ClientError as e:
            LOG.debug(e)
            # if the error is because the resource was not found, be quiet
            if "NotFound" not in e.response["Error"]["Code"]:
                raise
        return []

    class Meta(object):
        service = "ecr"
        type = "registery"
        id = "registryId"


class Repository(AWSResource):
    @classmethod
    def enumerate(cls, arn, region, account, resource_id=None, **kwargs):
        client = get_awsclient(cls.Meta.service, region, account, **kwargs)
        try:
            param = {"registryId": account}
            if resource_id and resource_id != "*":
                param.update({"repositoryNames": [resource_id]})
            data = client.call("describe_repositories", query="repositories[]", **param)

            if data:
                if "ResponseMetadata" in data:
                    del data["ResponseMetadata"]

                return map(lambda d: Repository(client, d, arn.query), data)
        except ClientError as e:
            LOG.debug(e)
            # if the error is because the resource was not found, be quiet
            if "NotFound" not in e.response["Error"]["Code"]:
                raise
        return []

    class Meta(object):
        service = "ecr"
        type = "repository"
        id = "repositoryName"

    def __init__(self, client, data, query=None):
        super(Repository, self).__init__(client, data, query)

    @property
    def arn(self):
        return self._data["repositoryArn"]