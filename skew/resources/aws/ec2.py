# Copyright (c) 2014 Mitch Garnaat http://garnaat.org/
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

from skew.resources.aws import AWSResource


class Instance(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'instance'
        enum_spec = ('DescribeInstances', 'Reservations[].Instances[]')
        detail_spec = None
        id = 'InstanceId'
        filter_name = 'instance_ids'
        name = 'PublicDnsName'
        date = 'LaunchTime'
        dimension = 'InstanceId'

    @property
    def parent(self):
        return self.data['ImageId']


class SecurityGroup(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'security-group'
        enum_spec = ('DescribeSecurityGroups', 'SecurityGroups')
        detail_spec = None
        id = 'GroupId'
        filter_name = 'group_names'
        name = 'GroupName'
        date = None
        dimension = None
