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
import datetime

import jmespath

from skew.arn.endpoint import Endpoint
from skew.utils import DynamicLoader

LOG = logging.getLogger(__name__)


def _keyfn(cls):
    key = None
    if getattr(cls, 'Config', None):
        key = cls.Config['type']
    return key

loader = DynamicLoader(_keyfn, __file__)


def find_resource_class(resource_type):
    return loader.find_class(resource_type)


def all_resource_types():
    return loader.all_keys()


def all_resources_for_service(service_name):
    return [name for name, cls in loader.all_items()
            if cls.Config['service'] == service_name]


def all_resource_classes():
    return loader.all_classes()


class MetricData(object):

    def __init__(self, data, period):
        self.data = data
        self.period = period


class Resource(object):
    """
    Each Resource class defines a Config variable at the class level.  This
    is a dictionary that gives the specifics about which service the resource
    belongs to and how to enumerate the resource.

    Each entry in the dictionary we define:

    * service - The AWS service in which this resource is defined.
    * enum_spec - The enumeration configuration.  This is a tuple consisting
      of the name of the operation to call to enumerate the resources and
      a jmespath query that will be run against the result of the operation
      to retrieve the list of resources.
    * detail_spec - Some services provide only summary information in the
      list or describe method and require you to make another request to get
      the detailed info for a specific resource.  If that is the case, this
      would contain a tuple consisting of the operation to call for the
      details, the parameter name to pass in to identify the desired
      resource and the jmespath filter to apply to the results to get
      the details.
    * id - The name of the field within the resource data that uniquely
      identifies the resource.
    * dimension - The CloudWatch dimension for this resource.  A value
      of None indicates that this resource is not monitored by CloudWatch.
    * filter_name - By default, the enumerator returns all resources of a
      given type.  But you can also tell it to filter the results by
      passing in a list of id's.  This parameter tells it the name of the
      parameter to use to specify this list of id's.
    """

    Config = {'type': 'resource'}

    def __init__(self, endpoint, data):
        self._endpoint = endpoint
        self._region = endpoint.region
        self._account = endpoint.account
        if data is None:
            data = {}
        self.data = data
        if 'id' in self.Config and isinstance(self.data, dict):
            self._id = self.data.get(self.Config['id'], '')
        else:
            self._id = ''
        self._cloudwatch = None
        if self.Config.get('dimension'):
            cloudwatch = self._endpoint.service.session.get_service(
                'cloudwatch')
            self._cloudwatch = Endpoint(
                cloudwatch, self._region, self._account)
        self._metrics = None
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
        return self.Config.get('type')

    @property
    def parent(self):
        pass

    @property
    def name(self):
        if not self._name:
            self._name = jmespath.search(self.Config['name'], self.data)
        return self._name

    @property
    def id(self):
        return self._id

    @property
    def date(self):
        if not self._date:
            self._date = jmespath.search(self.Config['date'], self.data)
        return self._date

    @property
    def metrics(self):
        if self._metrics is None:
            if self._cloudwatch:
                data = self._cloudwatch.call(
                    'ListMetrics',
                    dimensions=[{'Name': self.Config['dimension'],
                                 'Value': self._id}])
                self._metrics = jmespath.search('Metrics', data)
            else:
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

    def _total_seconds(self, delta):
        # python2.6 does not have timedelta.total_seconds() so we have
        # to calculate this ourselves.  This is straight from the
        # datetime docs.
        return ((delta.microseconds + (delta.seconds + delta.days * 24 * 3600)
                 * 10 ** 6) / 10 ** 6)

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
        if not statistics:
            statistics = ['Average']
        if days:
            delta = datetime.timedelta(days=days)
        elif hours:
            delta = datetime.timedelta(hours=hours)
        else:
            delta = datetime.timedelta(minutes=minutes)
        if not period:
            period = max(60, self._total_seconds(delta) // 1440)
        metric = self.find_metric(metric_name)
        if metric and self._cloudwatch:
            end = datetime.datetime.utcnow()
            start = end - delta
            data = self._cloudwatch.call(
                'GetMetricStatistics',
                dimensions=metric['Dimensions'],
                namespace=metric['Namespace'],
                metric_name=metric['MetricName'],
                start_time=start.isoformat(), end_time=end.isoformat(),
                statistics=statistics, period=period)
            return MetricData(jmespath.search('Datapoints', data), period)
        else:
            raise ValueError('Metric (%s) not available' % metric_name)

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
