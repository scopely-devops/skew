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
import unittest
import os

import mock

from skew import scan
from tests.unit.mock_awsclient import get_awsclient
import skew.awsclient

skew.awsclient.get_awsclient = get_awsclient


class TestARN(unittest.TestCase):

    def setUp(self):
        self.environ = {}
        self.environ_patch = mock.patch('os.environ', self.environ)
        self.environ_patch.start()
        credential_path = os.path.join(os.path.dirname(__file__), 'cfg',
                                       'aws_credentials')
        self.environ['AWS_CONFIG_FILE'] = credential_path
        config_path = os.path.join(os.path.dirname(__file__), 'cfg',
                                   'skew.yml')
        self.environ['SKEW_CONFIG'] = config_path

    def tearDown(self):
        pass

    def test_ec2_instance(self):
        arn = scan('arn:aws:ec2:us-west-2:123456789012:instance/*')
        # Fetch all Instance resources
        l = list(arn)
        self.assertEqual(len(l), 2)
        # Fetch non-existant resource
        arn = scan('arn:aws:ec2:us-west-2:123456789012:instance/i-decafbad')
        l = list(arn)
        self.assertEqual(len(l), 0)
        # Fetch a single resource
        arn = scan('arn:aws:ec2:us-west-2:123456789012:instance/i-30f39af5')
        l = list(arn)
        self.assertEqual(len(l), 1)
        # check filters
        arn = scan('arn:aws:ec2:us-west-2:123456789012:instance/i-30f39af5|InstanceType')
        l = list(arn)
        self.assertEqual(len(l), 1)
        r = l[0]
        self.assertEqual(r.filtered_data, 't2.small')

    def test_ec2_volumes(self):
        arn = scan('arn:aws:ec2::234567890123:volume/*')
        l = list(arn)
        self.assertEqual(len(l), 1)
        r = l[0]
        self.assertEqual(r.data['VolumeId'], "vol-ea3e1724")

    def test_ec2_images(self):
        arn = scan('arn:aws:ec2:us-west-2:234567890123:image/*')
        l = list(arn)
        self.assertEqual(len(l), 1)

    def test_ec2_keypairs(self):
        arn = scan('arn:aws:ec2:*:234567890123:key-pair/*')
        l = list(arn)
        self.assertEqual(len(l), 2)

    def test_ec2_securitygroup(self):
        arn = scan('arn:aws:ec2:*:123456789012:security-group/*')
        l = list(arn)
        self.assertEqual(len(l), 10)

    def test_elb_loadbalancer(self):
        arn = scan('arn:aws:elb:us-west-2:123456789012:loadbalancer/*')
        l = list(arn)
        self.assertEqual(len(l), 1)
        arn = scan('arn:aws:elb:us-west-2:234567890123:loadbalancer/*')
        l = list(arn)
        self.assertEqual(len(l), 5)

    def test_ec2_vpcs(self):
        arn = scan('arn:aws:ec2:us-west-2:123456789012:vpc/*')
        l = list(arn)
        self.assertEqual(len(l), 2)

    def test_ec2_routetable(self):
        arn = scan('arn:aws:ec2:us-west-2:123456789012:route-table/*')
        l = list(arn)
        self.assertEqual(len(l), 3)

    def test_ec2_network_acls(self):
        arn = scan('arn:aws:ec2:us-west-2:123456789012:network-acl/*')
        l = list(arn)
        self.assertEqual(len(l), 4)

    def test_iam_users(self):
        arn = scan('arn:aws:iam:*:234567890123:user/*')
        l = list(arn)
        self.assertEqual(len(l), 3)
        arn = scan('arn:aws:iam:*:234567890123:user/foo')
        l = list(arn)
        self.assertEqual(len(l), 1)

    def test_s3_buckets(self):
        arn = scan('arn:aws:s3:us-east-1:234567890123:bucket/*')
        l = list(arn)
        self.assertEqual(len(l), 4)
        bucket_resource = l[1]
        keys = list(bucket_resource)
        self.assertEqual(len(keys), 4)

    def test_iam_groups(self):
        arn = scan('arn:aws:iam::123456789012:group/*')
        l = list(arn)
        self.assertEqual(len(l), 2)
        group_resource = l[0]
        self.assertEqual(group_resource.arn,
                         'arn:aws:iam::123456789012:group/Administrators')

    def test_route53_hostedzone(self):
        arn = scan('arn:aws:route53::123456789012:hostedzone/*')
        l = list(arn)
        self.assertEqual(len(l), 2)
        zone_resource = l[0]
        self.assertEqual(zone_resource.arn,
                         'arn:aws:route53:::hostedzone/FFFF865FFFF3')

    def test_cloudformation_stacks(self):
        arn = scan('arn:aws:cloudformation:us-west-2:123456789012:stack/*')
        l = list(arn)
        self.assertEqual(len(l), 1)
        stack_resource = l[0]
        resources = list(stack_resource)
        self.assertEqual(len(resources), 6)
