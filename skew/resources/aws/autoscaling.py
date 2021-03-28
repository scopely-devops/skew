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

from skew.resources.aws import AWSResource
from skew.awsclient import get_awsclient


class AutoScalingGroup(AWSResource):
    class Meta(object):
        service = "autoscaling"
        type = "autoScalingGroup"
        name = "AutoScalingGroupName"
        date = "CreatedTime"
        dimension = "AutoScalingGroupName"
        enum_spec = ("describe_auto_scaling_groups", "AutoScalingGroups", None)
        detail_spec = None
        id = "AutoScalingGroupName"
        filter_name = "AutoScalingGroupNames"
        filter_type = "list"

    def __init__(self, client, data, query=None):
        super(AutoScalingGroup, self).__init__(client, data, query)
        self._arn_query = jmespath.compile("AutoScalingGroupARN")

    @property
    def arn(self):
        return self._arn_query.search(self.data)

    def sleek(self):
        # Always render lists in the same order to avoid false changes detection
        self.data["EnabledMetrics"].sort(key=lambda item: item["Metric"])
        self.data["SuspendedProcesses"].sort(key=str)

    @classmethod
    def set_tags(cls, arn, region, account, tags, resource_id=None, **kwargs):
        client = get_awsclient(cls.Meta.service, region, account, **kwargs)
        asg_name = arn.split(":")[7].split("/")[1]
        addon = dict(
            ResourceId=asg_name,
            ResourceType="auto-scaling-group",
            PropagateAtLaunch=False,
        )
        tags_list = [dict(Key=k, Value=str(v), **addon) for k, v in tags.items()]
        return client.call("create_or_update_tags", Tags=tags_list)

    @classmethod
    def unset_tags(cls, arn, region, account, tag_keys, resource_id=None, **kwargs):
        client = get_awsclient(cls.Meta.service, region, account, **kwargs)
        asg_name = arn.split(":")[7].split("/")[1]
        addon = dict(
            ResourceId=asg_name,
            ResourceType="auto-scaling-group",
            PropagateAtLaunch=False,
        )
        tags_list = [dict(Key=k, **addon) for k in tag_keys]
        return client.call("delete_tags", Tags=tags_list)


class LaunchConfiguration(AWSResource):
    class Meta(object):
        service = "autoscaling"
        type = "launchConfiguration"
        name = "LaunchConfigurationName"
        date = "CreatedTime"
        dimension = "AutoScalingGroupName"
        enum_spec = ("describe_launch_configurations", "LaunchConfigurations", None)
        detail_spec = None
        id = "LaunchConfigurationName"
        filter_name = "LaunchConfigurationNames"
        filter_type = "list"

    def __init__(self, client, data, query=None):
        super(LaunchConfiguration, self).__init__(client, data, query)
        self._arn_query = jmespath.compile("LaunchConfigurationARN")

    @property
    def arn(self):
        return self._arn_query.search(self.data)
