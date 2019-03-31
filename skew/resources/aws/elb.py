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
        service = 'elb'
        type = 'loadbalancer'
        enum_spec = ('describe_load_balancers',
                     'LoadBalancerDescriptions', None)
        detail_spec = None
        attr_spec = [
            ('describe_load_balancer_attributes', 'LoadBalancerName',
                'LoadBalancerAttributes'),
            ('describe_load_balancer_policies', 'LoadBalancerName',
                'PolicyDescriptions'),
        ]
        id = 'LoadBalancerName'
        filter_name = 'LoadBalancerNames'
        filter_type = 'list'
        name = 'DNSName'
        date = 'CreatedTime'
        dimension = 'LoadBalancerName'
        tags_spec = ('describe_tags', 'TagDescriptions[].Tags[]',
                     'LoadBalancerNames', 'id')

    def __init__(self, client, data, query=None):
        super(LoadBalancer, self).__init__(client, data, query)

        self._id = data['LoadBalancerName']
        
        # add addition attribute data
        for attr in self.Meta.attr_spec:
            detail_op, param_name, detail_path = attr
            params = {param_name: self._id}
            data = client.call(detail_op, **params)
            self.data[detail_path] = jmespath.search(detail_path, data)
