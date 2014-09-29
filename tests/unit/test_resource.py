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
import unittest
import os

import botocore
import mock

import skew.resources
from skew.resources.resource import Resource
from skew.arn.endpoint import Endpoint


class FooResource(Resource):

    class Meta(object):
        service = 'ec2'
        type = 'foo'
        id = 'bar'


class TestResource(unittest.TestCase):

    def setUp(self):
        self.environ = {}
        self.environ_patch = mock.patch('os.environ', self.environ)
        self.environ_patch.start()
        config_path = os.path.join(os.path.dirname(__file__), 'cfg',
                                   'aws_config')
        self.environ['AWS_CONFIG_FILE'] = config_path

    def tearDown(self):
        pass

    def test_resource(self):
        session = botocore.session.get_session()
        service = session.get_service('ec2')
        endpoint = Endpoint(service, 'us-east-1', '123456789012')
        resource = FooResource(endpoint, data={'bar': 'bar'})
        self.assertEqual(resource.id, 'bar')
        self.assertEqual(resource.__repr__(),
                         'arn:aws:ec2:us-east-1:123456789012:foo/bar')
        self.assertEqual(resource.metrics, [])
        self.assertEqual(resource.find_metric('foobar'), None)

    def test_all_providers(self):
        all_providers = skew.resources.all_providers()
        self.assertEqual(len(all_providers), 1)
        self.assertEqual(all_providers[0], 'aws')

    def test_all_services(self):
        all_providers = skew.resources.all_services('aws')
        self.assertEqual(len(all_providers), 9)
        
