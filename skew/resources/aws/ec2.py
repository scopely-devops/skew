# Copyright (c) 2014 Scopely, Inc.
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
        filter_type = 'list'
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
        filter_type = 'list'
        name = 'GroupName'
        date = None
        dimension = None


class KeyPair(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'key-pair'
        enum_spec = ('DescribeKeyPairs', 'KeyPairs')
        detail_spec = None
        id = 'KeyName'
        filter_name = 'key_names'
        name = 'KeyName'
        date = None
        dimension = None


class Address(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'address'
        enum_spec = ('DescribeAddresses', 'Addresses')
        detail_spec = None
        id = 'PublicIp'
        filter_name = 'public-ips'
        filter_type = 'list'
        name = 'PublicIp'
        date = None
        dimension = None


class Volume(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'volume'
        enum_spec = ('DescribeVolumes', 'Volumes')
        detail_spec = None
        id = 'VolumeId'
        filter_name = 'volume_ids'
        filter_type = 'list'
        name = 'VolumeId'
        date = 'createTime'
        dimension = 'VolumeId'

    @property
    def parent(self):
        if len(self.data['Attachments']):
            return self.data['Attachments'][0]['InstanceId']
        else:
            return None


class Snapshot(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'snapshot'
        enum_spec = ('DescribeSnapshots', 'Snapshots')
        detail_spec = None
        id = 'SnapshotId'
        filter_name = 'snapshot_ids'
        filter_type = 'list'
        name = 'SnapshotId'
        date = 'StartTime'
        dimension = None

    @property
    def parent(self):
        if self.data['VolumeId']:
            return self.data['VolumeId']
        else:
            return None
