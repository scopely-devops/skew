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


class MockAWSClient(object):

    def __init__(self, service_name, region_name, account_id):
        self.service_name = service_name
        self.region_name = region_name
        self.account_id = account_id

    def _get_stored_response(self, op_name):
        path = os.path.join(os.path.dirname(__file__), 'data',
                            self.service_name)
        path = os.path.join(path, self.region_name)
        path = os.path.join(path, self.account_id)
        path = os.path.join(path, '{}.json'.format(op_name))
        with open(path) as fp:
            data = json.load(fp)
        return data

    def call(self, op_name, **kwargs):
        return self._get_stored_response(op_name)


def get_awsclient(service_name, region_name, account_id):
    return MockAWSClient(service_name, region_name, account_id)
