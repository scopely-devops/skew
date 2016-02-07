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

import logging

from skew.resources.aws import AWSResource


LOG = logging.getLogger(__name__)


class IAMResource(AWSResource):

    @property
    def arn(self):
        return 'arn:aws:%s::%s:%s/%s' % (
            self._client.service_name,
            self._client.account_id, self.resourcetype, self.name)


class Group(IAMResource):

    class Meta(object):
        service = 'iam'
        type = 'group'
        enum_spec = ('list_groups', 'Groups', None)
        detail_spec = None
        id = 'GroupId'
        name = 'GroupName'
        filter_name = None
        date = 'CreateDate'
        dimension = None

    @classmethod
    def filter(cls, arn, resource_id, data):
        LOG.debug('%s == %s', resource_id, data)
        return resource_id == data['GroupName']


class User(IAMResource):

    class Meta(object):
        service = 'iam'
        type = 'user'
        enum_spec = ('list_users', 'Users', None)
        detail_spec = None
        id = 'UserId'
        filter_name = None
        name = 'UserName'
        date = 'CreateDate'
        dimension = None

    @classmethod
    def filter(cls, arn, resource_id, data):
        LOG.debug('%s == %s', resource_id, data)
        return resource_id == data['UserName']


class Role(IAMResource):

    class Meta(object):
        service = 'iam'
        type = 'role'
        enum_spec = ('list_roles', 'Roles', None)
        detail_spec = None
        id = 'RoleId'
        filter_name = None
        name = 'RoleName'
        date = 'CreateDate'
        dimension = None

    @classmethod
    def filter(cls, arn, resource_id, data):
        LOG.debug('%s == %s', resource_id, data)
        return resource_id == data['RoleName']


class InstanceProfile(IAMResource):

    class Meta(object):
        service = 'iam'
        type = 'instance-profile'
        enum_spec = ('list_instance_profiles', 'InstanceProfiles', None)
        detail_spec = None
        id = 'InstanceProfileId'
        filter_name = None
        name = 'InstanceProfileId'
        date = 'CreateDate'
        dimension = None

    @classmethod
    def filter(cls, arn, resource_id, data):
        LOG.debug('%s == %s', resource_id, data)
        return resource_id == data['InstanceProfileId']


class Policy(IAMResource):

    class Meta(object):
        service = 'iam'
        type = 'policy'
        enum_spec = ('list_policies', 'Policies', None)
        detail_spec = None
        id = 'PolicyId'
        filter_name = None
        name = 'PolicyName'
        date = 'CreateDate'
        dimension = None

    @classmethod
    def filter(cls, arn, resource_id, data):
        LOG.debug('%s == %s', resource_id, data)
        return resource_id == data['UserName']


class ServerCertificate(IAMResource):

    class Meta(object):
        service = 'iam'
        type = 'server-certificate'
        enum_spec = ('list_server_certificates',
                     'ServerCertificateMetadataList',
                     None)
        detail_spec = None
        id = 'ServerCertificateId'
        filter_name = None
        name = 'ServerCertificateName'
        date = 'Expiration'
        dimension = None

    @classmethod
    def filter(cls, arn, resource_id, data):
        LOG.debug('%s == %s', resource_id, data)
        return resource_id == data['ServerCertificateName']
