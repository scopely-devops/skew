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

import httpretty
import mock
import botocore.session

from skew import scan
from skew.arn.resources import Resource
from skew.arn.endpoint import Endpoint


class FooResource(Resource):

    Config = {
        'service': 'ec2',
        'type': 'foo',
        'id': 'bar'}


def get_response_body(name):
    path = os.path.join(os.path.dirname(__file__), 'data', name)
    fp = open(path)
    body = fp.read()
    fp.close()
    return body


def path(filename):
    return os.path.join(os.path.dirname(__file__), 'cfg', filename)


class TestARN(unittest.TestCase):

    def setUp(self):
        self.environ = {}
        self.environ_patch = mock.patch('os.environ', self.environ)
        self.environ_patch.start()
        config_path = os.path.join(os.path.dirname(__file__), 'cfg',
                                   'aws_config')
        self.environ['AWS_CONFIG_FILE'] = config_path

    def tearDown(self):
        pass

    @httpretty.activate
    def test_iam_user(self):
        # Set up the HTTP mocking
        host = 'https://iam.amazonaws.com/'
        body = get_response_body('iam_user.xml')
        httpretty.register_uri(httpretty.POST, host,
                               body=body,
                               status=200)
        # Run the test
        arn = scan('arn:aws:iam:us-east-1:123456789012:user/*')
        users = list(arn)
        self.assertEqual(len(users), 4)
        self.assertEqual(users[0].data['UserName'], 'foo')
        self.assertEqual(users[0].name, 'foo')
        self.assertEqual(users[3].date, '2013-08-08T21:50:58Z')

    # This callback will be associated with an event that gets fired
    # when new EC2 Instance resources are created.  It will store a
    # bogus attribute on each object and then we will look for them
    # in the test method to verify that its getting called.
    def _my_callback(self, event_name, resource, **kwargs):
        resource.__foobar__ = 'fiebaz'

    @httpretty.activate
    def test_ec2_instance(self):
        # Set up the HTTP mocking
        host = 'https://ec2.us-east-1.amazonaws.com/'
        body1 = get_response_body('ec2_instance.xml')
        body2 = get_response_body('instance_not_found.xml')
        body3 = get_response_body('one_instance.xml')
        httpretty.register_uri(httpretty.POST, host,
                               responses=[
                                   httpretty.Response(body=body1, status=200),
                                   httpretty.Response(body=body2, status=400),
                                   httpretty.Response(body=body3, status=200),
                               ])
        host = 'https://monitoring.us-east-1.amazonaws.com/'
        body1 = get_response_body('instance_metric_names.xml')
        body2 = get_response_body('get_metric_data.xml')
        httpretty.register_uri(httpretty.POST, host,
                               responses=[
                                   httpretty.Response(body=body1, status=200),
                                   httpretty.Response(body=body2, status=200),
                               ])
        # Run the test
        arn = scan('arn:aws:ec2:us-east-1:123456789012:instance/*')
        # Register our local event handler
        arn.register_for_event('resource-create.aws.ec2.*.*.instance.*',
                               self._my_callback)
        # Fetch all Instance resources
        instances = list(arn)
        self.assertEqual(len(instances), 2)
        # Check to see if our callback got called
        for i in instances:
            self.assertEqual(getattr(i, '__foobar__'), 'fiebaz')
        # Fetch non-existant resource
        arn = scan('arn:aws:ec2:us-east-1:123456789012:instance/i-decafbad')
        instances = list(arn)
        self.assertEqual(len(instances), 0)
        # Fetch a single instance
        arn = scan('arn:aws:ec2:us-east-1:123456789012:instance/i-123456789')
        instances = list(arn)
        self.assertEqual(len(instances), 1)
        instance = instances[0]
        # Find available metrics
        self.assertEqual(len(instance.metric_names), 10)
        self.assertEqual(instance.metric_names,
                         ['DiskReadOps',
                          'NetworkOut',
                          'DiskWriteOps',
                          'DiskReadBytes',
                          'CPUUtilization',
                          'StatusCheckFailed',
                          'StatusCheckFailed_System',
                          'StatusCheckFailed_Instance',
                          'NetworkIn',
                          'DiskWriteBytes'])
        # Fetch metric data
        metric = instance.get_metric_data('CPUUtilization')
        self.assertEqual(metric.period, 60)
        self.assertEqual(len(metric.data), 12)
        self.assertEqual(metric.data[-1]['Average'], 0.0)
        self.assertEqual(instance.date, '2013-04-25T23:41:15.000Z')
        self.assertEqual(instance.name, 'foo.bar.com')

    @httpretty.activate
    def test_dynamodb_table(self):
        # Set up the HTTP mocking
        content_type = 'application/x-amz-json-1.0'
        host = 'https://dynamodb.us-east-1.amazonaws.com/'
        body1 = get_response_body('dynamodb_tables.json')
        body2 = get_response_body('table_one.json')
        body3 = get_response_body('table_two.json')
        httpretty.register_uri(httpretty.POST, host,
                               responses=[
                                   httpretty.Response(
                                       body=body1, status=200,
                                       content_type=content_type),
                                   httpretty.Response(
                                       body=body2, status=200,
                                       content_type=content_type),
                                   httpretty.Response(
                                       body=body3, status=200,
                                       content_type=content_type),
                               ])
        # Run the test
        arn = scan('arn:aws:dynamodb:us-east-1:123456789012:table/*')
        # Fetch all Table resources
        tables = list(arn)
        self.assertEqual(len(tables), 2)
        t = tables[0]
        self.assertEqual(t.name, 'foo')
        self.assertEqual(t.date, 1368642592.791)
        t = tables[1]
        self.assertEqual(t.name, 'bar')
        self.assertEqual(t.date, 1368642593.791)

    @httpretty.activate
    def test_autoscale_group(self):
        # Set up the HTTP mocking
        host = 'https://autoscaling.us-east-1.amazonaws.com/'
        body = get_response_body('autoscale_asg.xml')
        httpretty.register_uri(httpretty.POST, host,
                               body=body,
                               status=200)
        # Run the test
        arn = scan('arn:aws:autoscaling:us-east-1:123456789012:autoScalingGroup/*')
        asgs = list(arn)
        self.assertEqual(len(asgs), 2)
        self.assertEqual(asgs[0].data['AutoScalingGroupName'], 'foo')
        self.assertEqual(asgs[1].data['AutoScalingGroupName'], 'bar')

    @httpretty.activate
    def test_cloudwatch_alarm(self):
        # Set up the HTTP mocking
        host = 'https://monitoring.us-east-1.amazonaws.com/'
        body = get_response_body('cloudwatch_alarm.xml')
        httpretty.register_uri(httpretty.POST, host,
                               body=body,
                               status=200)
        # Run the test
        arn = scan('arn:aws:cloudwatch:us-east-1:123456789012:alarm/*')
        alarms = list(arn)
        self.assertEqual(len(alarms), 2)
        self.assertEqual(alarms[0].data['AlarmName'],
                         'UserLevel-ReadCapacityUnitsLimit-foo')
        self.assertEqual(alarms[1].data['AlarmName'],
                         'UserLevel-WriteCapacityUnitsLimit-bar')

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
        with self.assertRaises(ValueError) as cm:
            resource.get_metric_data('foobar', days=1)
