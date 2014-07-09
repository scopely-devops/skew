# Copyright (c) 2014 Mitch Garnaat http://garnaat.org/
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

LOG = logging.getLogger(__name__)


class Resource(object):

    class Meta(object):
        type = 'resource'

    def __init__(self, endpoint, data):
        self._endpoint = endpoint
        self._region = endpoint.region
        self._account = endpoint.account
        if data is None:
            data = {}
        self.data = data
        if hasattr(self.Meta, 'id') and isinstance(self.data, dict):
            self._id = self.data.get(self.Meta.id, '')
        else:
            self._id = ''
        self._metrics = list()
        self._name = None
        self._date = None

    def __repr__(self):
        return self.arn

    @property
    def arn(self):
        return 'arn:aws:%s:%s:%s:%s/%s' % (
            self._endpoint.service.endpoint_prefix,
            self._region, self._account, self.resourcetype, self.id)

    @property
    def resourcetype(self):
        return self.Meta.type

    @property
    def parent(self):
        pass

    @property
    def name(self):
        if not self._name:
            self._name = jmespath.search(self.Meta.name, self.data)
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def date(self):
        if not self._date:
            self._date = jmespath.search(self.Meta.date, self.data)
        return self._date

    @property
    def metrics(self):
        if self._metrics is None:
            self._metrics = []
        return self._metrics

    @property
    def metric_names(self):
        return [m['MetricName'] for m in self.metrics]

    def find_metric(self, metric_name):
        for m in self.metrics:
            if m['MetricName'] == metric_name:
                return m
        return None

    def get_metric_data(self, metric_name, days=None, hours=1, minutes=None,
                        statistics=None, period=None):
        """
        Get metric data for this resource.  You can specify the time
        frame for the data as either the number of days or number of
        hours.  The maximum window is 14 days.  Based on the time frame
        this method will calculate the correct ``period`` to return
        the maximum number of data points up to the CloudWatch max
        of 1440.

        :type metric_name: str
        :param metric_name: The name of the metric this data will
            pertain to.

        :type days: int
        :param days: The number of days worth of data to return.
            You can specify either ``days`` or ``hours``.  The default
            is one hour.  The maximum value is 14 days.

        :type hours: int
        :param hours: The number of hours worth of data to return.
            You can specify either ``days`` or ``hours``.  The default
            is one hour.  The maximum value is 14 days.

        :type statistics: list of str
        :param statistics: The metric statistics to return.  The default
            value is **Average**.  Possible values are:

            * Average
            * Sum
            * SampleCount
            * Maximum
            * Minimum
        """
        pass

    def summary(self, metric_name):
        return self.get_metric_data(
            metric_name, days=14,
            statistics=['Average', 'Maximum', 'SampleCount'],
            period=self.max_period)

    def tail(self, metric_name):
        return self.get_metric_data(
            metric_name, days=None, hours=None, minutes=5,
            statistics=['Average', 'Maximum', 'SampleCount'],
            period=self.max_period)
