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

from skew.resources.aws import AWSResource


class Instance(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'instance'
        enum_spec = ('describe_instances', 'Reservations[].Instances[]', None)
        detail_spec = None
        id = 'InstanceId'
        filter_name = 'InstanceIds'
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
        enum_spec = ('describe_security_groups', 'SecurityGroups', None)
        detail_spec = None
        id = 'GroupId'
        filter_name = 'GroupNames'
        filter_type = 'list'
        name = 'GroupName'
        date = None
        dimension = None


class KeyPair(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'key-pair'
        enum_spec = ('describe_key_pairs', 'KeyPairs', None)
        detail_spec = None
        id = 'KeyPairId'
        filter_name = 'KeyNames'
        name = 'KeyName'
        date = None
        dimension = None


class Address(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'address'
        enum_spec = ('describe_addresses', 'Addresses', None)
        detail_spec = None
        id = 'AllocationId'
        filter_name = 'PublicIps'
        filter_type = 'list'
        name = 'PublicIp'
        date = None
        dimension = None


class Volume(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'volume'
        enum_spec = ('describe_volumes', 'Volumes', None)
        detail_spec = None
        id = 'VolumeId'
        filter_name = 'VolumeIds'
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
        enum_spec = (
            'describe_snapshots', 'Snapshots', {'OwnerIds': ['self']})
        detail_spec = None
        id = 'SnapshotId'
        filter_name = 'SnapshotIds'
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


class Image(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'image'
        enum_spec = (
            'describe_images', 'Images', {'Owners': ['self']})
        detail_spec = None
        id = 'ImageId'
        filter_name = 'ImageIds'
        filter_type = 'list'
        name = 'ImageId'
        date = 'StartTime'
        dimension = None

    @property
    def parent(self):
        if self.data['VolumeId']:
            return self.data['VolumeId']
        else:
            return None


class Vpc(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'vpc'
        enum_spec = ('describe_vpcs', 'Vpcs', None)
        detail_spec = None
        id = 'VpcId'
        filter_name = 'VpcIds'
        filter_type = 'list'
        name = 'VpcId'
        date = None
        dimension = None


class Subnet(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'subnet'
        enum_spec = ('describe_subnets', 'Subnets', None)
        detail_spec = None
        id = 'SubnetId'
        filter_name = 'SubnetIds'
        filter_type = 'list'
        name = 'SubnetId'
        date = None
        dimension = None


class CustomerGateway(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'customer-gateway'
        enum_spec = ('describe_customer_gateways', 'CustomerGateways', None)
        detail_spec = None
        id = 'CustomerGatewayId'
        filter_name = 'CustomerGatewayIds'
        filter_type = 'list'
        name = 'CustomerGatewayId'
        date = None
        dimension = None


class InternetGateway(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'internet-gateway'
        enum_spec = ('describe_internet_gateways', 'InternetGateways', None)
        detail_spec = None
        id = 'InternetGatewayId'
        filter_name = 'InternetGatewayIds'
        filter_type = 'list'
        name = 'InternetGatewayId'
        date = None
        dimension = None


class RouteTable(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'route-table'
        enum_spec = ('describe_route_tables', 'RouteTables', None)
        detail_spec = None
        id = 'RouteTableId'
        filter_name = 'RouteTableIds'
        filter_type = 'list'
        name = 'RouteTableId'
        date = None
        dimension = None


class NatGateway(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'natgateway'
        enum_spec = ('describe_nat_gateways', 'NatGateways', None)
        detail_spec = None
        id = 'NatGatewayId'
        filter_name = 'NatGatewayIds'
        filter_type = 'list'
        name = 'NatGatewayId'
        date = 'CreateTime'
        dimension = None


class NetworkAcl(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'network-acl'
        enum_spec = ('describe_network_acls', 'NetworkAcls', None)
        detail_spec = None
        id = 'NetworkAclId'
        filter_name = 'NetworkAclIds'
        filter_type = 'list'
        name = 'NetworkAclId'
        date = None
        dimension = None


class VpcPeeringConnection(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'vpc-peering-connection'
        enum_spec = ('describe_vpc_peering_connections',
                     'VpcPeeringConnections', None)
        detail_spec = None
        id = 'VpcPeeringConnectionId'
        filter_name = 'VpcPeeringConnectionIds'
        filter_type = 'list'
        name = 'VpcPeeringConnectionId'
        date = None
        dimension = None


class LaunchTemplate(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'launch-template'
        enum_spec = ('describe_launch_templates', 'LaunchTemplates', None)
        detail_spec = None
        id = 'LaunchTemplateId'
        filter_name = 'LaunchTemplateIds'
        filter_type = 'list'
        name = 'LaunchTemplateName'
        date = 'CreateTime'
        dimension = None


class FlowLog(AWSResource):

    class Meta(object):
        service = 'ec2'
        type = 'flow-log'
        enum_spec = ('describe_flow_logs', 'FlowLogs', None)
        detail_spec = None
        id = 'FlowLogId'
        filter_name = 'FlowLogIds'
        filter_type = 'list'
        name = 'LogGroupName'
        date = 'CreationTime'
        dimension = None
