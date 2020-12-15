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
import placebo

from skew import scan


class TestARN(unittest.TestCase):
    def _get_response_path(self, test_case):
        p = os.path.join(os.path.dirname(__file__), "responses")
        return os.path.join(p, test_case)

    def setUp(self):
        self.environ = {}
        self.environ_patch = mock.patch("os.environ", self.environ)
        self.environ_patch.start()
        credential_path = os.path.join(
            os.path.dirname(__file__), "cfg", "aws_credentials"
        )
        self.environ["AWS_CONFIG_FILE"] = credential_path
        config_path = os.path.join(os.path.dirname(__file__), "cfg", "skew.yml")
        self.environ["SKEW_CONFIG"] = config_path

    def tearDown(self):
        pass

    def test_ec2(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("instances_1"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:ec2:us-west-2:123456789012:instance/*", **placebo_cfg)
        # Fetch all Instance resources
        l = list(arn)
        self.assertEqual(len(l), 2)
        # Fetch a single resource
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("instances_2"),
            "placebo_mode": "playback",
        }
        arn = scan(
            "arn:aws:ec2:us-west-2:123456789012:instance/i-db530902", **placebo_cfg
        )
        l = list(arn)
        self.assertEqual(len(l), 1)
        # check filters
        arn = scan(
            "arn:aws:ec2:us-west-2:123456789012:instance/i-db530902|InstanceType",
            **placebo_cfg
        )
        l = list(arn)
        self.assertEqual(len(l), 1)
        r = l[0]
        self.assertEqual(r.filtered_data, "t2.small")

    def test_ec2_instance_not_found(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("instances_3"),
            "placebo_mode": "playback",
        }
        arn = scan(
            "arn:aws:ec2:us-west-2:123456789012:instance/i-87654321", **placebo_cfg
        )
        # Fetch all Instance resources
        l = list(arn)
        self.assertEqual(len(l), 0)

    def test_ec2_volumes(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("volumes"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:ec2:us-west-2:123456789012:volume/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 4)
        r = l[0]
        self.assertEqual(r.data["VolumeId"], "vol-b85e475f")

    # def test_ec2_images(self):
    #     arn = scan('arn:aws:ec2:us-west-2:234567890123:image/*')
    #     l = list(arn)
    #     self.assertEqual(len(l), 1)

    def test_ec2_keypairs(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("keypairs"),
            "placebo_mode": "playback",
        }
        arn = scan(
            "arn:aws:ec2:us-west-2:123456789012:key-pair/*", debug=True, **placebo_cfg
        )
        l = list(arn)
        self.assertEqual(len(l), 2)
        self.assertEqual(l[0].id, "key-1274ea12942819e24")
        self.assertEqual(l[1].id, "key-1274ea12942819e25")
        self.assertEqual(l[0].name, "admin")
        self.assertEqual(l[1].name, "FooBar")
        self.assertEqual(
            l[0].data["KeyFingerprint"],
            "85:83:08:25:fa:96:45:ea:c9:15:04:12:af:45:3f:c0:ef:e8:b8:ce",
        )

    def test_ec2_securitygroup(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("secgrp"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:ec2:us-west-2:123456789012:security-group/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 3)

    def test_elb_loadbalancer(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("elbs"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:elb:us-east-1:123456789012:loadbalancer/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 1)
        self.assertEqual(
            l[0].arn, "arn:aws:elb:us-east-1:123456789012:loadbalancer/example"
        )
        self.assertEqual(
            l[0].data["DNSName"], "example-1111111111.us-east-1.elb.amazonaws.com"
        )
        self.assertEqual(l[0].tags["Name"], "example-web")
        self.assertEqual(
            l[0].data["LoadBalancerAttributes"]["CrossZoneLoadBalancing"]["Enabled"],
            False,
        )
        self.assertEqual(
            l[0].data["PolicyDescriptions"][0]["PolicyName"],
            "AWSConsole-SSLNegotiationPolicy-example-1111111111111",
        )

    def test_ec2_vpcs(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("vpcs"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:ec2:us-west-2:123456789012:vpc/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 3)

    def test_ec2_routetable(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("routetables"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:ec2:us-west-2:123456789012:route-table/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 5)

    def test_ec2_network_acls(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("networkacls"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:ec2:us-west-2:123456789012:network-acl/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 8)

    def test_s3_buckets(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("buckets"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:s3:us-east-1:234567890123:bucket/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 5)

    def test_iam_groups(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("groups"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:iam::234567890123:group/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 3)
        group_resource = l[0]
        self.assertEqual(
            group_resource.arn, "arn:aws:iam::234567890123:group/Administrators"
        )

    def test_iam_users(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("users"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:iam::123456789012:user/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 1)
        self.assertEqual(l[0].arn, "arn:aws:iam::123456789012:user/testuser")
        self.assertEqual(l[0].data["UserName"], "testuser")
        self.assertEqual(l[0].tags["TestKey"], "TestValue")
        self.assertEqual(
            l[0].data["AccessKeyMetadata"][0]["AccessKeyId"], "AKIAAAAAAAAAAAAAAAAA"
        )
        self.assertEqual(l[0].data["Groups"][0]["GroupId"], "AGPAAAAAAAAAAAAAAAAAA")
        self.assertEqual(
            l[0].data["PolicyNames"]["TestInlinePolicy"]["Version"], "2012-10-17"
        )
        self.assertEqual(
            l[0].data["AttachedPolicies"][0]["PolicyArn"],
            "arn:aws:iam::aws:policy/AdministratorAccess",
        )
        self.assertEqual(
            l[0].data["SSHPublicKeys"][0]["SSHPublicKeyId"], "APKAAAAAAAAAAAAAAAAA"
        )

    def test_cloudformation_stacks(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("stacks"),
            "placebo_mode": "playback",
        }
        arn = scan(
            "arn:aws:cloudformation:us-west-2:123456789012:stack/*", **placebo_cfg
        )
        l = list(arn)
        self.assertEqual(len(l), 1)
        stack_resource = l[0]
        resources = list(stack_resource)
        self.assertEqual(len(resources), 4)

    def test_nat_gateways(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("natgateways"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:ec2:us-west-2:123456789012:natgateway/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 1)
        natgateways = l[0]
        self.assertEqual(
            natgateways.arn,
            "arn:aws:ec2:us-west-2:123456789012:natgateway/nat-443d3ea762d00ee83",
        )

    def test_ec2_launchtemplates(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("launchtemplates"),
            "placebo_mode": "playback",
        }
        arn = scan(
            "arn:aws:ec2:us-west-2:123456789012:launch-template/*",
            debug=True,
            **placebo_cfg
        )
        l = list(arn)
        self.assertEqual(len(l), 4)
        self.assertEqual(l[0].id, "lt-000005555511111888")
        self.assertEqual(l[1].id, "lt-000007777744444999")
        self.assertEqual(l[2].id, "lt-000006666633333888")
        self.assertEqual(l[3].id, "lt-000777772222211223")

        self.assertEqual(l[1].data["Tags"][0]["Key"], "costcenter")
        self.assertTrue("Tags" not in l[3].data)

    def test_acm(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("certificates"),
            "placebo_mode": "playback",
        }
        arn = scan(
            "arn:aws:acm:us-west-2:123456789012:certificate/*",
            debug=True,
            **placebo_cfg
        )
        l = list(arn)
        self.assertEqual(len(l), 2)
        self.assertEqual(
            l[0].arn,
            "arn:aws:acm:us-west-2:123456789012:certificate/aaaaaaaa-bbbb-cccc-dddd-000000000001",
        )
        self.assertEqual(l[0].data["DomainName"], "example.com")
        self.assertEqual(l[0].tags["tld"], ".com")
        self.assertEqual(
            l[1].arn,
            "arn:aws:acm:us-west-2:123456789012:certificate/aaaaaaaa-bbbb-cccc-dddd-000000000002",
        )
        self.assertEqual(l[1].data["DomainName"], "example.net")
        self.assertEqual(l[1].tags["tld"], ".net")

    def test_cloudwatch_loggroup(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("loggroups"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:logs:us-east-1:123456789012:log-group/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 1)
        self.assertEqual(
            l[0].arn,
            "arn:aws:logs:us-east-1:123456789012:log-group:CloudTrail/DefaultLogGroup",
        )
        self.assertEqual(l[0].data["logGroupName"], "CloudTrail/DefaultLogGroup")
        self.assertEqual(l[0].tags["TestKey"], "TestValue")

        self.assertNotIn("logStreams", l[0].data)
        l[0].log_streams
        self.assertEqual(
            l[0].data["logStreams"][0]["logStreamName"],
            "123456789012_CloudTrail_us-east-1",
        )

        self.assertNotIn("metricFilters", l[0].data)
        l[0].metric_filters
        self.assertEqual(l[0].data["metricFilters"][0]["filterName"], "EventCount")

        self.assertNotIn("subscriptionFilters", l[0].data)
        l[0].subscriptions
        self.assertEqual(
            l[0].data["subscriptionFilters"][0]["filterName"], "TestLambdaTrigger"
        )

        self.assertNotIn("queries", l[0].data)
        l[0].queries
        self.assertEqual(
            l[0].data["queries"][0]["queryId"], "11111111-cfe3-43db-8eca-8862fee615a3"
        )

    def test_vpc_flowlog(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("flowlogs"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:ec2:us-east-1:123456789012:flow-log/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 2)
        self.assertEqual(
            l[0].arn, "arn:aws:ec2:us-east-1:123456789012:flow-log/fl-1234abcd"
        )
        self.assertEqual(l[0].data["LogGroupName"], "CloudTrail/DefaultLogGroup")
        self.assertEqual(str(l[0].data["CreationTime"]), "2017-01-23 19:47:49+00:00")

    def test_cloudtrail(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("trail"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:cloudtrail:us-east-1:123456789012:trail/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 1)
        print(l[0].tags)
        self.assertEqual(
            l[0].arn, "arn:aws:cloudtrail:us-east-1:123456789012:trail/awslog"
        )
        self.assertEqual(
            l[0].data["CloudWatchLogsLogGroupArn"],
            "arn:aws:logs:us-east-1:123456789012:log-group:CloudTrail/DefaultLogGroup:*",
        )
        print(l[0].tags)
        self.assertEqual(l[0].tags["TestKey"], "TestValue")

    def test_no_provider(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("trail"),
            "placebo_mode": "playback",
        }
        arn = scan("::cloudtrail:us-east-1:123456789012:trail/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 1)

    def test_alarm(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("alarms"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:cloudwatch:us-east-1:123456789012:alarm/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 1)
        self.assertEqual(
            l[0].arn, "arn:aws:cloudwatch:us-east-1:123456789012:alarm:some-alarm"
        )
        self.assertEqual(
            l[0].data["AlarmArn"],
            "arn:aws:cloudwatch:us-east-1:123456789012:alarm:some-alarm",
        )

    def test_customer_gateway(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("customergateways"),
            "placebo_mode": "playback",
        }
        arn = scan(
            "arn:aws:ec2:us-east-1:123456789012:customer-gateway/*", **placebo_cfg
        )
        l = list(arn)
        self.assertEqual(len(l), 1)
        self.assertEqual(
            l[0].arn,
            "arn:aws:ec2:us-east-1:123456789012:customer-gateway/cgw-030d9af8cdbcdc12f",
        )
        self.assertEqual(l[0].data["CustomerGatewayId"], "cgw-030d9af8cdbcdc12f")

    def test_beanstalk_environments(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("environments"),
            "placebo_mode": "playback",
        }
        arn = scan(
            "arn:aws:elasticbeanstalk:us-west-2:123456789012:environment/*",
            **placebo_cfg
        )
        l = list(arn)
        r = l[0]
        self.assertEqual(r.data["EnvironmentName"], "Env1")
        self.assertEqual(
            r.arn,
            "arn:aws:elasticbeanstalk:us-west-2:123456789012:environment/sample-application/Env1",
        )
        self.assertEqual(r.data["ApplicationName"], "sample-application")

    def test_ec2_address(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("addresses"),
            "placebo_mode": "playback",
        }
        arn = scan("arn:aws:ec2:us-east-1:123456789012:address/*", **placebo_cfg)
        l = list(arn)
        self.assertEqual(len(l), 3)
        self.assertEqual(
            l[0].arn,
            "arn:aws:ec2:us-east-1:123456789012:address/eipalloc-091f2b843804f008c",
        )
        self.assertEqual(l[0].data["AllocationId"], "eipalloc-091f2b843804f008c")

        self.assertEqual(
            l[2].data["Tags"],
            [{"Key": "Name", "Value": "some-name"}, {"Key": "Env", "Value": "Prod"}],
        )

    def test_vpc_peering_connection(self):
        placebo_cfg = {
            "placebo": placebo,
            "placebo_dir": self._get_response_path("peeringconnections"),
            "placebo_mode": "playback",
        }
        arn = scan(
            "arn:aws:ec2:us-east-1:123456789012:vpc-peering-connection/*", **placebo_cfg
        )
        l = list(arn)
        self.assertEqual(len(l), 1)
        self.assertEqual(
            l[0].arn,
            "arn:aws:ec2:us-east-1:123456789012:vpc-peering-connection/pcx-027a582b95db2af78",
        )
