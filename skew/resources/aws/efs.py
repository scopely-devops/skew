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
from skew.awsclient import get_awsclient


LOG = logging.getLogger(__name__)


class Filesystem(AWSResource):

    class Meta(object):
        service = 'efs'
        type = 'filesystem'
        resourcegroups_tagging = False
        enum_spec = ('describe_file_systems', 'FileSystems', None)
        detail_spec = None
        id = 'FileSystemId'
        tags_spec = ('describe_tags', 'Tags[]',
                     'FileSystemId', 'id')
        filter_name = None
        name = 'Name'
        date = 'CreationTime'
        dimension = None

    @property
    def arn(self):
        # arn:aws:elasticfilesystem:us-east-1:123456789012:file-system-id/fs12345678
        return 'arn:aws:%s:%s:%s:%s/%s' % (
            'elasticfilesystem',
            self._client.region_name,
            self._client.account_id,
            'file-system-id', self.id)

    def sleek(self):
        self.data['SizeInBytes'] = 0
