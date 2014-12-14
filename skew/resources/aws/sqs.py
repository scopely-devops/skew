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


class Queue(AWSResource):

    class Meta(object):
        service = 'sqs'
        type = 'queue'
        enum_spec = ('ListQueues', 'QueueUrls')
        detail_spec = ('GetQueueAttributes', 'queue_url', 'QueueUrl')
        id = 'QueueUrl'
        filter_name = 'queue_name_prefix'
        filter_type = 'scalar'
        name = 'QueueUrl'
        date = None
        dimension = 'QueueName'

    def __init__(self, endpoint, data, query=None):
        super(Queue, self).__init__(endpoint, data, query)
        self.data = {self.Meta.id: data,
                     'QueueName': data.split('/')[-1]}
        self._id = self.data['QueueName']
