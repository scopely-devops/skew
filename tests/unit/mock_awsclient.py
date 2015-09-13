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

import os
import json
import logging

LOG = logging.getLogger(__name__)


class MockAWSClient(object):

    def __init__(self, service_name, region_name, account_id):
        self.service_name = service_name
        self.region_name = region_name
        self.account_id = account_id

    def _get_stored_response(self, op_name, kwargs):
        LOG.debug('op_name={}, kwargs={}'.format(op_name, kwargs))
        data = {}
        path = os.path.join(os.path.dirname(__file__), 'data',
                            self.service_name)
        if self.service_name not in ('iam', 'route53'):
            path = os.path.join(path, self.region_name)
        path = os.path.join(path, self.account_id)
        filename = op_name
        if kwargs:
            for k, v in kwargs.items():
                if k != 'query':
                    filename += '_{}_{}'.format(k, v)
        filename += '.json'
        path = os.path.join(path, filename)
        try:
            with open(path) as fp:
                data = json.load(fp)
        except IOError:
            LOG.debug('path: {} not found'.format(path))
        return data

    def call(self, op_name, **kwargs):
        return self._get_stored_response(op_name, kwargs)


def get_awsclient(service_name, region_name, account_id):
    return MockAWSClient(service_name, region_name, account_id)
