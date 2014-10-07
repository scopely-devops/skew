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


class DBInstance(AWSResource):

    class Meta(object):
        service = 'rds'
        type = 'dbinstance'
        enum_spec = ('DescribeDBInstances', 'DBInstances')
        tags_spec = ('ListTagsForResource', 'TagList', 'resource_name', 'arn')
        detail_spec = None
        id = 'DBInstanceIdentifier'
        filter_name = 'db_instance_identifier'
        filter_type = 'scalar'
        name = 'Endpoint.Address'
        date = 'InstanceCreateTime'
        dimension = 'DBInstanceIdentifier'


class DBSecurityGroup(AWSResource):

    class Meta(object):
        service = 'rds'
        type = 'dbsecuritygroup'
        enum_spec = ('DescribeDBSecurityGroups', 'DBSecurityGroups')
        detail_spec = None
        id = 'DBSecurityGroupName'
        filter_name = 'db_security_group_name'
        filter_type = 'scalar'
        name = 'DBSecurityGroupDescription'
        date = None
        dimension = None
