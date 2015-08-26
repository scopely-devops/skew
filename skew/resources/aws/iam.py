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


class Group(AWSResource):

    class Meta(object):
        service = 'iam'
        type = 'group'
        enum_spec = ('list_groups', 'Groups', None)
        detail_spec = None
        id = 'GroupName'
        name = 'GroupName'
        filter_name = None
        date = 'CreateDate'
        dimension = None

    @classmethod
    def filter(cls, resource_id, data):
        LOG.debug('%s == %s', resource_id, data)
        return resource_id == data['GroupName']


class User(AWSResource):

    class Meta(object):
        service = 'iam'
        type = 'user'
        enum_spec = ('list_users', 'Users', None)
        detail_spec = None
        id = 'UserName'
        filter_name = None
        name = 'UserName'
        date = 'CreateDate'
        dimension = None

    @classmethod
    def filter(cls, resource_id, data):
        LOG.debug('%s == %s', resource_id, data)
        return resource_id == data['UserName']


class ServerCertificate(AWSResource):

    class Meta(object):
        service = 'iam'
        type = 'server-certificate'
        enum_spec = ('list_server_certificates',
                     'ServerCertificateMetadataList',
                     None)
        detail_spec = None
        id = 'ServerCertificateName'
        filter_name = None
        name = 'ServerCertificateName'
        date = 'Expiration'
        dimension = None

    @classmethod
    def filter(cls, resource_id, data):
        LOG.debug('%s == %s', resource_id, data)
        return resource_id == data['ServerCertificateName']
        
