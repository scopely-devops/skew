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
from skew.awsclient import get_awsclient


class Queue(AWSResource):

    class Meta(object):
        service = 'sqs'
        type = 'queue'
        resourcegroups_tagging = False
        enum_spec = ('list_queues', 'QueueUrls', None)
        detail_spec = ('get_queue_attributes', 'QueueUrl', 'QueueUrl')
        id = 'QueueUrl'
        filter_name = 'QueueNamePrefix'
        filter_type = 'scalar'
        name = 'QueueName'
        date = None
        dimension = 'QueueName'
        tags_spec = None

    def __init__(self, client, data, query=None):
        super(Queue, self).__init__(client, data, query)
        self.data = {self.Meta.id: data,
                     'QueueName': data.split('/')[-1]}
        self._id = self.data['QueueName']
        response = client.call('list_queue_tags',
                               QueueUrl=self.data['QueueUrl'])
        self._tags = response.get('Tags', {})

    @property
    def arn(self):
        return 'arn:aws:sqs:%s:%s:%s' % (
            self._client.region_name,
            self._client.account_id, self.id)

    @classmethod
    def set_tags(cls, arn, region, account, tags, resource_id=None, **kwargs):
        queue_name = arn.split(':')[5]
        queue_url = 'https://sqs.{}.amazonaws.com/{}/{}'.format(region,
                                                                account,
                                                                queue_name)
        client = get_awsclient(
            cls.Meta.service, region, account, **kwargs)
        return client.call('tag_queue',
                           QueueUrl=queue_url,
                           Tags=tags)

    @classmethod
    def unset_tags(cls, arn, region, account, tag_keys, resource_id=None, **kwargs):
        queue_name = arn.split(':')[5]
        queue_url = 'https://sqs.{}.amazonaws.com/{}/{}'.format(region,
                                                                account,
                                                                queue_name)
        client = get_awsclient(
            cls.Meta.service, region, account, **kwargs)
        return client.call('untag_queue',
                           QueueUrl=queue_url,
                           TagKeys=tag_keys)
