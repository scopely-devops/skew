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


class Topic(AWSResource):

    class Meta(object):
        service = 'sns'
        type = 'topic'
        enum_spec = ('list_topics', 'Topics', None)
        detail_spec = ('get_topic_attributes', 'TopicArn', 'Attributes')
        id = 'TopicArn'
        filter_name = None
        filter_type = None
        name = 'DisplayName'
        date = None
        dimension = 'TopicName'
        tags_spec = ('list_tags_for_resource', 'Tags[]', 'ResourceArn', 'arn')

    @classmethod
    def filter(cls, arn, resource_id, data):
        topic_arn = data.get(cls.Meta.id)
        LOG.debug('%s == %s', arn, topic_arn)
        return arn == topic_arn

    @property
    def arn(self):
        return self.data.get('TopicArn')

    def __init__(self, client, data, query=None):
        super(Topic, self).__init__(client, data, query)

        self._id = data['TopicArn'].split(':', 5)[5]

        detail_op, param_name, detail_path = self.Meta.detail_spec
        params = {param_name: data['TopicArn']}
        data = client.call(detail_op, **params)

        self.data = jmespath.search(detail_path, data)


class Subscription(AWSResource):

    invalid_arns = ['PendingConfirmation', 'Deleted']

    class Meta(object):
        service = 'sns'
        type = 'subscription'
        enum_spec = ('list_subscriptions', 'Subscriptions', None)
        detail_spec = ('get_subscription_attributes', 'SubscriptionArn',
                       'Attributes')
        id = 'SubscriptionArn'
        filter_name = None
        filter_type = None
        name = 'SubscriptionArn'
        date = None
        dimension = None

    @property
    def arn(self):
        return self.data.get('SubscriptionArn')

    @classmethod
    def enumerate(cls, arn, region, account, resource_id=None, **kwargs):
        resources = super(Subscription, cls).enumerate(
            arn, region, account, resource_id, **kwargs)

        return [r for r in resources if r.id not in cls.invalid_arns]

    def __init__(self, client, data, query=None):
        super(Subscription, self).__init__(client, data, query)

        if data['SubscriptionArn'] in self.invalid_arns:
            self._id = 'PendingConfirmation'
            return

        self._id = data['SubscriptionArn'].split(':', 6)[6]
        self._name = ""

        detail_op, param_name, detail_path = self.Meta.detail_spec
        params = {param_name: data['SubscriptionArn']}
        data = client.call(detail_op, **params)

        self.data = jmespath.search(detail_path, data)
