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

import jmespath

from skew.resources.aws import AWSResource


class LoadBalancer(AWSResource):

    class Meta(object):
        service = 'elbv2'
        type = 'loadbalancer'
        enum_spec = ('describe_load_balancers',
                     'LoadBalancers', None)
        # detail_spec = None
        detail_spec = ('describe_listeners', 'LoadBalancerArn', 'Listeners')
        id = 'LoadBalancerArn'
        filter_name = 'Names'
        filter_type = 'list'
        name = 'LoadBalancerName'
        date = 'CreatedTime'
        dimension = None
        tags_spec = ('describe_tags', 'TagDescriptions[].Tags[]',
                     'ResourceArns', 'id')

    @property
    def arn(self):
        return self.data['LoadBalancerArn']

    def __init__(self, client, data, query=None):
        super(LoadBalancer, self).__init__(client, data, query)
        detail_op, param_name, detail_path = self.Meta.detail_spec
        params = {param_name: self.data['LoadBalancerArn']}
        data = client.call(detail_op, **params)
        self.data['Listeners'] = jmespath.search(detail_path, data)


class TargetGroup(AWSResource):

    class Meta(object):
        service = 'elbv2'
        type = 'targetgroup'
        enum_spec = ('describe_target_groups',
                     'TargetGroups', None)
        detail_spec = None
        id = 'TargetGroupArn'
        filter_name = 'Names'
        filter_type = 'list'
        name = 'TargetGroupName'
        date = 'CreatedTime'
        dimension = 'LoadBalancerName'
        tags_spec = ('describe_tags', 'TagDescriptions[].Tags[]',
                     'LoadBalancerNames', 'id')

    @property
    def arn(self):
        return self.data['TargetGroupArn']
