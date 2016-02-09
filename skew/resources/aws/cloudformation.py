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
import jmespath

from skew.resources.aws import AWSResource


class Stack(AWSResource):

    @classmethod
    def enumerate(cls, arn, region, account, resource_id=None, **kwargs):
        resources = super(Stack, cls).enumerate(arn, region, account,
                                                resource_id, **kwargs)
        for stack in resources:
            stack.data['Resources'] = []
            for stack_resource in stack:
                resource_id = stack_resource.get('PhysicalResourceId')
                if not resource_id:
                    resource_id = stack_resource.get('LogicalResourceId')
                stack.data['Resources'].append(
                    {
                        'id': resource_id,
                        'type': stack_resource['ResourceType']
                    }
                )
        return resources

    class Meta(object):
        service = 'cloudformation'
        type = 'stack'
        enum_spec = ('describe_stacks', 'Stacks[]', None)
        detail_spec = ('describe_stack_resources', 'StackName',
                       'StackResources[]')
        id = 'StackName'
        filter_name = 'StackName'
        name = 'StackName'
        date = 'CreationTime'
        dimension = None

    def __init__(self, client, data, query=None):
        super(Stack, self).__init__(client, data, query)
        self._data = data
        self._resources = []

    def __iter__(self):
        detail_op, param_name, detail_path = self.Meta.detail_spec
        params = {param_name: self.id}
        if not self._resources:
            data = self._client.call(detail_op, **params)
            self._resources = jmespath.search(detail_path, data)
        for resource in self._resources:
            yield resource

    @property
    def arn(self):
        return self._data['StackId']
