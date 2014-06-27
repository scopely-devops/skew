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

import skew.arn.resources


class DBInstance(skew.arn.resources.Resource):

    class Meta(object):
        service = 'rds'
        type = 'dbinstance'
        enum_spec = ('DescribeDBInstances', 'DBInstances')
        detail_spec = None
        id = 'DBInstanceIdentifier'
        filter_name = 'db_instance_identfier'
        name = 'Endpoint.Address'
        date = 'InstanceCreateTime'
        dimension = 'DBInstanceIdentifier'


class DBSecurityGroup(skew.arn.resources.Resource):

    class Meta(object):
        service = 'rds'
        type = 'dbsecuritygroup'
        enum_spec = ('DescribeDBSecurityGroups', 'DBSecurityGroups')
        detail_spec = None
        id = 'DBSecurityGroupName'
        filter_name = 'db_security_group_name'
        name = 'DBSecurityGroupDescription'
        date = None
        dimension = None
