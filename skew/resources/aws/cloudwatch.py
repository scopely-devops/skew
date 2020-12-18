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
import jmespath
import logging
from skew.resources.aws import AWSResource

LOG = logging.getLogger(__name__)


class Alarm(AWSResource):
    class Meta(object):
        service = "cloudwatch"
        type = "alarm"
        enum_spec = ("describe_alarms", "MetricAlarms", None)
        id = "AlarmName"
        filter_name = "AlarmNames"
        filter_type = None
        detail_spec = None
        name = "AlarmName"
        date = "AlarmConfigurationUpdatedTimestamp"
        dimension = None
        tags_spec = ("list_tags_for_resource", "Tags[]", "ResourceARN", "arn")

    @property
    def arn(self):
        return "arn:aws:%s:%s:%s:%s:%s" % (
            self._client.service_name,
            self._client.region_name,
            self._client.account_id,
            self.resourcetype,
            self.id,
        )


class LogGroup(AWSResource):
    class Meta(object):
        service = "logs"
        type = "log-group"
        enum_spec = ("describe_log_groups", "logGroups[]", None)
        attr_spec = {
            "logStreams": ("describe_log_streams", "logStreams", "logGroupName", "id"),
            "metricFilters": (
                "describe_metric_filters",
                "metricFilters",
                "logGroupName",
                "id",
            ),
            "queries": ("describe_queries", "queries", "logGroupName", "id"),
            "subscription": (
                "describe_subscription_filters",
                "subscriptionFilters",
                "logGroupName",
                "id",
            ),
        }

        detail_spec = None
        id = "logGroupName"
        tags_spec = ("list_tags_log_group", "tags", "logGroupName", "id")
        filter_name = "logGroupNamePrefix"
        filter_type = "dict"
        name = "logGroupName"
        date = "creationTime"
        dimension = "logGroupName"

    def __init__(self, client, data, query=None):
        super(LogGroup, self).__init__(client, data, query)
        self._keys = []
        self._id = data["logGroupName"]

    @property
    def log_streams(self):
        if "logStreams" not in self._data:
            self._data["logStreams"] = self._remove_response_metadata(
                self._feed_from_spec(attr_spec=self.Meta.attr_spec["logStreams"])
            )
        return self._data["logStreams"]

    @property
    def metric_filters(self):
        if "metricFilters" not in self._data:
            self._data["metricFilters"] = self._remove_response_metadata(
                self._feed_from_spec(attr_spec=self.Meta.attr_spec["metricFilters"])
            )
        return self._data["metricFilters"]

    @property
    def queries(self):
        if "queries" not in self._data:
            self._data["queries"] = self._remove_response_metadata(
                self._feed_from_spec(attr_spec=self.Meta.attr_spec["queries"])
            )
        return self._data["queries"]

    @property
    def subscriptions(self):
        if "subscriptionFilters" not in self._data:
            self._data["subscriptionFilters"] = self._remove_response_metadata(
                self._feed_from_spec(attr_spec=self.Meta.attr_spec["subscription"])
            )
        return self._data["subscriptionFilters"]

    def _remove_response_metadata(self, data):
        if "ResponseMetadata" in data:
            del data["ResponseMetadata"]
        return data

    @property
    def logGroupName(self):
        return self.data.get("logGroupName")

    @property
    def arn(self):
        return "arn:aws:%s:%s:%s:%s:%s" % (
            self._client.service_name,
            self._client.region_name,
            self._client.account_id,
            self.resourcetype,
            self.id,
        )


class CloudWatchEventRule(AWSResource):
    class Meta(object):
        service = "events"
        type = "rule"
        enum_spec = ("list_rules", "Rules[]", None)
        id = "Name"
        filter_name = None
        filter_type = None
        name = "Name"
        attr_spec = ("list_targets_by_rule", "Targets[]", "Rule", "id")
        # tags_spec = ("list_tags_log_group", "tags", "logGroupName", "id")

    @classmethod
    def filter(cls, arn, resource_id, data):
        return resource_id == data["None"]

    def __init__(self, client, data, query=None):
        super(CloudWatchEventRule, self).__init__(client, data, query)
        self._data["Targets"] = self._feed_from_spec(attr_spec=self.Meta.attr_spec)
