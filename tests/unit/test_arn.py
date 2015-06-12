# Copyright (c) 2014 Scopely, Inc.
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

from skew import scan


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

    @httpretty.activate
    def test_iam_user_filtering(self):
        # Set up the HTTP mocking
        host = 'https://iam.amazonaws.com/'
        body = get_response_body('iam_user.xml')
        httpretty.register_uri(httpretty.POST, host,
                               body=body,
                               status=200)
        # Run the test
        arn = scan('arn:aws:iam:us-east-1:123456789012:user/bar')
        users = list(arn)
        self.assertEqual(len(users), 1)
        self.assertEqual(users[0].data['UserName'], 'bar')
        self.assertEqual(users[0].name, 'bar')

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
        # Fetch all Instance resources
        instances = list(arn)
        self.assertEqual(len(instances), 2)
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
        metric_data = instance.get_metric_data('CPUUtilization')
        self.assertEqual(len(metric_data.data), 12)
        self.assertEqual(metric_data.data[-1]['Average'], 0.0)
        self.assertEqual(instance.name, 'foo.bar.com')
        # Fetch tags
        self.assertEqual(list(instance.tags.keys()), ['Name'])
        self.assertEqual(list(instance.tags.values()), ['foo'])

    @httpretty.activate
    def test_jmespath_query(self):
        # Set up the HTTP mocking
        host = 'https://ec2.us-east-1.amazonaws.com/'
        body = get_response_body('one_instance.xml')
        httpretty.register_uri(httpretty.POST, host,
                               body=body)
        # Run the test
        arn = scan('arn:aws:ec2:us-east-1:123456789012:instance/*|InstanceType')
        # Fetch all Instance resources
        instances = list(arn)
        self.assertEqual(len(instances), 1)
        # Check to see if filtered data is there
        self.assertEqual(instances[0].filtered_data, 'c1.medium')

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
        t = tables[1]
        self.assertEqual(t.name, 'bar')

    @httpretty.activate
    def test_dynamodb_filtering(self):
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
        arn = scan('arn:aws:dynamodb:us-east-1:123456789012:table/foo')
        # Fetch all Table resources
        tables = list(arn)
        self.assertEqual(len(tables), 1)
        t = tables[0]
        self.assertEqual(t.name, 'foo')

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

    @httpretty.activate
    def test_ec2_volume(self):
        # Set up the HTTP mocking
        host = 'https://ec2.us-east-1.amazonaws.com/'
        body = get_response_body('ec2_volumes.xml')
        httpretty.register_uri(httpretty.POST, host,
                               body=body,
                               status=200)
        # Run the test
        arn = scan('arn:aws:ec2:us-east-1:123456789012:volume/*')
        vols = list(arn)
        self.assertEqual(len(vols), 2)
        self.assertEqual(vols[0].data['VolumeId'], 'vol-27d4da72')
        self.assertEqual(vols[0].parent, 'i-734d643c')
        self.assertEqual(vols[0].tags['Owner'], 'bob')
        self.assertEqual(vols[1].data['Size'], 10)
        self.assertEqual(vols[1].parent, None)

    @httpretty.activate
    def test_load_balancers(self):
        # Set up the HTTP mocking
        host = 'https://elasticloadbalancing.us-east-1.amazonaws.com/'
        body1 = get_response_body('elb.xml')
        body2 = get_response_body('elb_tags.xml')
        httpretty.register_uri(httpretty.POST, host,
                               responses=[
                                   httpretty.Response(
                                       body=body1, status=200),
                                   httpretty.Response(
                                       body=body2, status=200)])
        # Run the test
        arn = scan('arn:aws:elb:us-east-1:123456789012:*')
        elbs = list(arn)
        self.assertEqual(len(elbs), 2)
        elb = elbs[0]
        self.assertEqual(elb.data['LoadBalancerName'], 'proxy')
        self.assertEqual(len(elb.data['Instances']), 2)
        self.assertEqual(elb.data['Instances'][0]['InstanceId'], 'i-123eb1c6')
        self.assertEqual(elb.data['ListenerDescriptions'][0]['Listener']['LoadBalancerPort'], 3128)
        self.assertEqual(len(elb.tags), 4)
        self.assertEqual(elb.tags['Environment'], 'PRODUCTION')
        self.assertEqual(elb.tags['Owner'], 'bob')

    @httpretty.activate
    def test_rds_dbinstance(self):
        # Set up the HTTP mocking
        host = 'https://rds.amazonaws.com/'
        body1 = get_response_body('rds_one_instance.xml')
        body2 = get_response_body('rds_tags.xml')
        httpretty.register_uri(httpretty.POST, host,
                               responses=[
                                   httpretty.Response(body=body1, status=200),
                                   httpretty.Response(body=body1, status=200),
                                   httpretty.Response(body=body2, status=200),
                               ])
        # Run the test
        arn = scan('arn:aws:rds:us-east-1:123456789012:db/*')
        # Fetch all DB resources
        dbs = list(arn)
        self.assertEqual(len(dbs), 1)
        # Fetch a single instance
        arn = scan('arn:aws:rds:us-east-1:123456789012:db/foobar')
        dbs = list(arn)
        self.assertEqual(len(dbs), 1)
        db = dbs[0]
        # Fetch tags
        self.assertEqual(db.tags['Allocation'], 'research')
        self.assertEqual(db.tags['Name'], 'foobar')

    @httpretty.activate
    def test_rds_security_group(self):
        # Set up the HTTP mocking
        host = 'https://rds.amazonaws.com/'
        body1 = get_response_body('rds_secgrp.xml')
        httpretty.register_uri(httpretty.POST, host,
                               responses=[
                                   httpretty.Response(body=body1, status=200),
                                   httpretty.Response(body=body1, status=200),
                               ])
        # Run the test
        arn = scan('arn:aws:rds:us-east-1:123456789012:secgrp/*')
        # Fetch all resources
        secgrps = list(arn)
        self.assertEqual(len(secgrps), 1)
        # Fetch a single resource
        arn = scan('arn:aws:rds:us-east-1:123456789012:secgrp/foo')
        secgrps = list(arn)
        self.assertEqual(len(secgrps), 1)

    @httpretty.activate
    def test_kinesis_streams(self):
        # Set up the HTTP mocking
        content_type = 'application/x-amz-json-1.1'
        host = 'https://kinesis.us-east-1.amazonaws.com/'
        body1 = get_response_body('kinesis_streams.json')
        httpretty.register_uri(httpretty.POST, host,
                               responses=[
                                   httpretty.Response(
                                       body=body1, status=200,
                                       content_type=content_type),
                               ])
        # Run the test
        arn = scan('arn:aws:kinesis:us-east-1:123456789012:stream/*')
        # Fetch all stream resources
        tables = list(arn)
        self.assertEqual(len(tables), 4)
        t = tables[0]
        self.assertEqual(t.name, 'foo')
        self.assertEqual(t.id, 'foo')
        t = tables[1]
        self.assertEqual(t.name, 'bar')
        self.assertEqual(t.id, 'bar')

    @httpretty.activate
    def test_sqs_queues(self):
        # Set up the HTTP mocking
        host = 'https://queue.amazonaws.com/'
        body1 = get_response_body('sqs_queues.xml')
        httpretty.register_uri(httpretty.POST, host,
                               responses=[
                                   httpretty.Response(
                                       body=body1, status=200)
                               ])
        # Run the test
        arn = scan('arn:aws:sqs:us-east-1:123456789012:queue/*')
        # Fetch all queue resources
        queues = list(arn)
        self.assertEqual(len(queues), 4)
        q = queues[0]
        self.assertEqual(q.id, 'foo')
        self.assertEqual(
            q.name, 'https://queue.amazonaws.com/123456789012/foo')
        q = queues[1]
        self.assertEqual(
            q.name, 'https://queue.amazonaws.com/123456789012/bar')
        self.assertEqual(q.id, 'bar')
        q = queues[2]
        self.assertEqual(
            q.name, 'https://queue.amazonaws.com/123456789012/fie')
        self.assertEqual(q.id, 'fie')
        q = queues[3]
        self.assertEqual(
            q.name, 'https://queue.amazonaws.com/123456789012/baz')
        self.assertEqual(q.id, 'baz')

    @httpretty.activate
    def test_s3_bucket_list(self):
        # Set up the HTTP mocking
        host = 'https://s3.amazonaws.com/'
        bucket = 'https://samples.s3.amazonaws.com'
        body1 = get_response_body('s3_bucket_list.xml')
        body2 = get_response_body('s3_bucket_keys.xml')
        httpretty.register_uri(httpretty.GET, host,
                               body=body1,
                               status=200)
        httpretty.register_uri(httpretty.GET, bucket,
                               body=body2,
                               status=200)
        # Run the test
        arn = scan('arn:aws:s3:us-east-1:123456789012:*')
        buckets = list(arn)
        self.assertEqual(len(buckets), 2)
        self.assertEqual(buckets[0].id, 'quotes')
        self.assertEqual(buckets[1].id, 'samples')

        keys = list(buckets[1])
        self.assertEqual(len(keys), 3)

        key_names = [x['Key'] for x in keys]
        key_list = ['my-image.jpg', 'my-second-image.jpg', 'my-third-image.jpg']
        self.assertEqual(sorted(key_names), sorted(key_list))
