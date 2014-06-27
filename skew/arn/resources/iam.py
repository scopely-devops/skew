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


class Group(skew.arn.resources.Resource):

    class Meta(object):
        service = 'iam'
        type = 'group'
        enum_spec = ('ListGroups', 'Groups')
        detail_spec = None
        id = 'GroupName'
        name = 'GroupName'
        filter_name = None
        date = 'CreateDate'
        dimension = None


class User(skew.arn.resources.Resource):

    class Meta(object):
        service = 'iam'
        type = 'user'
        enum_spec = ('ListUsers', 'Users')
        detail_spec = None
        id = 'UserName'
        filter_name = None
        name = 'UserName'
        date = 'CreateDate'
        dimension = None
