# Copyright (c) 2014 Scopely, Inc.
# Copyright (c) 2015 Mitch Garnaat
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

from skew.resources.aws import AWSResource


LOG = logging.getLogger(__name__)


class Cluster(AWSResource):
    class Meta(object):
        service = "ecs"
        type = "cluster"
        enum_spec = ("list_clusters", "clusterArns", None)
        detail_spec = ("describe_clusters", "clusters", "clusters[0]")
        id = None
        tags_spec = ("list_tags_for_resource", "tags[]", "resourceArn", "arn")

        filter_name = None
        name = "clusterName"
        date = None
        dimension = None

        attr_spec = ("list_services", "serviceArns[]", "cluster", "id")

    @property
    def arn(self):
        return self.data["clusterArn"]

    def __init__(self, client, data, query=None):
        super(Cluster, self).__init__(client, data, query)
        self._id = data
        detail_op, param_name, detail_path = self.Meta.detail_spec
        params = {param_name: [self.id]}
        data = client.call(detail_op, **params)
        self._data = jmespath.search(detail_path, data)

        service_arns = self._feed_from_spec(attr_spec=self.Meta.attr_spec)
        self._data["services"] = {}
        for service_arn in service_arns:
            kwargs = {
                "cluster": self._id,
                "services": [service_arn],
                "include": ["TAGS"],
            }
            service_def = self._client.call(
                "describe_services", query="services[0]", **kwargs
            )
            self._data["services"][service_def["serviceName"]] = service_def


class TaskDefinition(AWSResource):
    class Meta(object):
        service = "ecs"
        type = "task-definition"
        enum_spec = ("list_task_definitions", "taskDefinitionArns", None)
        detail_spec = ("describe_task_definition", "taskDefinition", "taskDefinition")
        id = None
        name = None
        filter_name = None
        date = None
        dimension = None

    def __init__(self, client, data, query=None):
        super(TaskDefinition, self).__init__(client, data, query)
        self._id = data
        detail_op, param_name, detail_path = self.Meta.detail_spec
        params = {param_name: self.id}
        data = client.call(detail_op, **params)
        self._data = jmespath.search(detail_path, data)

    @property
    def arn(self):
        return self._data["taskDefinitionArn"]
