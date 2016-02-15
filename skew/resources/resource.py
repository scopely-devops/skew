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

import skew.awsclient

from botocore.exceptions import ClientError

LOG = logging.getLogger(__name__)


class Resource(object):

    @classmethod
    def enumerate(cls, arn, region, account, resource_id=None, **kwargs):
        client = skew.awsclient.get_awsclient(
            cls.Meta.service, region, account, **kwargs)
        kwargs = {}
        do_client_side_filtering = False
        if resource_id and resource_id != '*':
            # If we are looking for a specific resource and the
            # API provides a way to filter on a specific resource
            # id then let's insert the right parameter to do the filtering.
            # If the API does not support that, we will have to filter
            # after we get all of the results.
            filter_name = cls.Meta.filter_name
            if filter_name:
                if cls.Meta.filter_type == 'list':
                    kwargs[filter_name] = [resource_id]
                else:
                    kwargs[filter_name] = resource_id
            else:
                do_client_side_filtering = True
        enum_op, path, extra_args = cls.Meta.enum_spec
        if extra_args:
            kwargs.update(extra_args)
        LOG.debug('enum_op=%s' % enum_op)
        try:
            data = client.call(enum_op, query=path, **kwargs)
        except ClientError as e:
            data = {}
            # if the error is because the resource was not found, be quiet
            if 'NotFound' not in e.response['Error']['Code']:
                raise
        LOG.debug(data)
        resources = []
        if data:
            for d in data:
                if do_client_side_filtering:
                    # If the API does not support filtering, the resource
                    # class should provide a filter method that will
                    # return True if the returned data matches the
                    # resource ID we are looking for.
                    if not cls.filter(arn, resource_id, d):
                        continue
                resources.append(cls(client, d, arn.query))
        return resources

    class Meta(object):
        type = 'resource'
        dimension = None
        tags_spec = None
        id = None
        date = None
        name = None

    def __init__(self, client, data):
        self._client = client
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
            self._client.service_name,
            self._client.region_name,
            self._client.account_id,
            self.resourcetype, self.id)

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
