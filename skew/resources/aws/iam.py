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
import jmespath
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
        detail_spec = ('get_user', 'UserName', 'User')
        attr_spec = [
            ('list_access_keys', 'UserName',
                'AccessKeyMetadata', 'AccessKeyMetadata'),
            ('list_groups_for_user', 'UserName',
                'Groups', 'Groups'),
            ('list_user_policies', 'UserName',
                'PolicyNames', 'PolicyNames'),
            ('list_attached_user_policies', 'UserName',
                'AttachedPolicies', 'AttachedPolicies'),
            ('list_ssh_public_keys', 'UserName',
                'SSHPublicKeys', 'SSHPublicKeys'),
            # ('list_mfa_devices', 'UserName', 'MFADevices', 'MFADevices'),
        ]
        id = 'UserId'
        filter_name = None
        name = 'UserName'
        date = 'CreateDate'
        dimension = None
        tags_spec = ('list_user_tags', 'Tags[]',
                     'UserName', 'name')

    def __init__(self, client, data, query=None):
        super(User, self).__init__(client, data, query)

        LOG.debug(data)
        # add details
        if self.Meta.detail_spec is not None:
            detail_op, param_name, detail_path = self.Meta.detail_spec
            params = {param_name: self.data[param_name]}
            data = client.call(detail_op, **params)
            self.data = jmespath.search(detail_path, data)

        # add attribute data
        if self.Meta.attr_spec is not None:
            for attr in self.Meta.attr_spec:
                LOG.debug(attr)
                LOG.debug(data)
                detail_op, param_name, detail_path, detail_key = attr
                params = {param_name: self.data[param_name]}
                tmp_data = self._client.call(detail_op, **params)
                if not (detail_path is None):
                    tmp_data = jmespath.search(detail_path, tmp_data)
                if 'ResponseMetadata' in tmp_data:
                    del tmp_data['ResponseMetadata']
                self.data[detail_key] = tmp_data
                LOG.debug(data)

            # retrieve all of the inline IAM policies
            if 'PolicyNames' in self.data \
                and self.data['PolicyNames']:
                tmp_dict = {}
                for policy_name in self.data['PolicyNames']:
                    params = {
                        'UserName': self.data['UserName'],
                        'PolicyName': policy_name
                    }
                    tmp_data = self._client.call('get_user_policy', **params)
                    tmp_data = jmespath.search('PolicyDocument', tmp_data)
                    tmp_dict[policy_name] = tmp_data
                self.data['PolicyNames'] = tmp_dict

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
        tags_spec = ('list_role_tags', 'Tags[]', 'RoleName', 'name')

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
        id = 'PolicyArn'
        filter_name = None
        name = 'PolicyName'
        date = 'CreateDate'
        dimension = None

    @classmethod
    def filter(cls, arn, resource_id, data):
        LOG.debug('%s == %s', resource_id, data)
        return resource_id == data['PolicyName']


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
