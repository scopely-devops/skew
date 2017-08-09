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


class Function(AWSResource):

    @classmethod
    def enumerate(cls, arn, region, account, resource_id=None, **kwargs):
        resources = super(Function, cls).enumerate(arn, region, account,
                                                   resource_id, **kwargs)
        for r in resources:
            r.data['EventSources'] = []
            kwargs = {'FunctionName': r.data['FunctionName']}
            response = r._client.call('list_event_source_mappings', **kwargs)
            for esm in response['EventSourceMappings']:
                r.data['EventSources'].append(esm['EventSourceArn'])
        return resources

    class Meta(object):
        service = 'lambda'
        type = 'function'
        enum_spec = ('list_functions', 'Functions', None)
        detail_spec = None
        id = 'FunctionName'
        filter_name = None
        name = 'FunctionName'
        date = 'LastModified'
        dimension = 'FunctionName'
        tags_spec = ('list_tags', 'Tags',
                     'Resource', 'arn')

    @classmethod
    def filter(cls, arn, resource_id, data):
        function_name = data.get(cls.Meta.id)
        LOG.debug('%s == %s', resource_id, function_name)
        return resource_id == function_name

    @property
    def arn(self):
        return self.data.get('FunctionArn')
