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
import jmespath
import logging
from skew.resources.aws import AWSResource

LOG = logging.getLogger(__name__)


class Alarm(AWSResource):

    class Meta(object):
        service = 'cloudwatch'
        type = 'alarm'
        enum_spec = ('describe_alarms', 'MetricAlarms', None)
        id = 'AlarmName'
        filter_name = 'AlarmNames'
        filter_type = None
        detail_spec = None
        name = 'AlarmName'
        date = 'AlarmConfigurationUpdatedTimestamp'
        dimension = None
        tags_spec = ('list_tags_for_resource', 'Tags[]', 'ResourceARN', 'arn')

    @property
    def arn(self):
        return 'arn:aws:%s:%s:%s:%s:%s' % (
            self._client.service_name,
            self._client.region_name,
            self._client.account_id,
            self.resourcetype, self.id)


class LogGroup(AWSResource):

    class Meta(object):
        service = 'logs'
        type = 'log-group'
        enum_spec = ('describe_log_groups', 'logGroups[]', None)
        attr_spec = [
            ('describe_log_streams', 'logGroupName',
             'logStreams', 'logStreams'),
            ('describe_metric_filters', 'logGroupName',
             'metricFilters', 'metricFilters'),
            ('describe_subscription_filters', 'logGroupName',
             'subscriptionFilters', 'subscriptionFilters'),
            ('describe_queries', 'logGroupName',
             'queries', 'queries'),
        ]
        detail_spec = None
        id = 'logGroupName'
        tags_spec = ('list_tags_log_group', 'tags',
                     'logGroupName', 'id')
        filter_name = 'logGroupNamePrefix'
        filter_type = 'dict'
        name = 'logGroupName'
        date = 'creationTime'
        dimension = 'logGroupName'

    def __init__(self, client, data, query=None):
        super(LogGroup, self).__init__(client, data, query)
        self._data = data
        self._keys = []
        self._id = data['logGroupName']

        # add addition attribute data
        for attr in self.Meta.attr_spec:
            LOG.debug(attr)
            detail_op, param_name, detail_path, detail_key = attr
            params = {param_name: self._id}
            data = self._client.call(detail_op, **params)
            if not (detail_path is None):
                data = jmespath.search(detail_path, data)
            if 'ResponseMetadata' in data:
                del data['ResponseMetadata']
            self.data[detail_key] = data
            LOG.debug(data)

    @property
    def logGroupName(self):
        return self.data.get('logGroupName')

    @property
    def arn(self):
        return 'arn:aws:%s:%s:%s:%s:%s' % (
            self._client.service_name,
            self._client.region_name,
            self._client.account_id, self.resourcetype, self.id)
