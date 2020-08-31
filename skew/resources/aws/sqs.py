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


class Queue(AWSResource):

    class Meta(object):
        service = 'sqs'
        type = 'queue'
        enum_spec = ('list_queues', 'QueueUrls', None)
        detail_spec = ('get_queue_attributes', 'QueueUrl', 'QueueUrl')
        id = 'QueueUrl'
        filter_name = 'QueueNamePrefix'
        filter_type = 'scalar'
        name = 'QueueUrl'
        date = None
        dimension = 'QueueName'
        tags_spec = ('list_queue_tags', 'Tags', 'QueueUrl', 'name')

    def __init__(self, client, data, query=None):
        super(Queue, self).__init__(client, data, query)
        self.data = {self.Meta.id: data,
                     'QueueName': data.split('/')[-1]}
        self._id = self.data['QueueName']
