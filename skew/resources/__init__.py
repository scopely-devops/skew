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

import importlib

# Maps resources names as they appear in ARN's to the path name
# of the Python class representing that resource.
ResourceTypes = {
    'aws.autoscaling.autoScalingGroup': 'aws.autoscaling.AutoScalingGroup',
    'aws.autoscaling.launchConfigurationName': 'aws.autoscaling.LaunchConfiguration',
    'aws.cloudwatch.alarm': 'aws.cloudwatch.Alarm',
    'aws.dynamodb.table': 'aws.dynamodb.Table',
    'aws.ec2.address': 'aws.ec2.Address',
    'aws.ec2.key-pair': 'aws.ec2.KeyPair',
    'aws.ec2.instance': 'aws.ec2.Instance',
    'aws.ec2.security-group': 'aws.ec2.SecurityGroup',
    'aws.ec2.snapshot': 'aws.ec2.Snapshot',
    'aws.ec2.volume': 'aws.ec2.Volume',
    'aws.elb.loadbalancer': 'aws.elb.LoadBalancer',
    'aws.iam.group': 'aws.iam.Group',
    'aws.iam.user': 'aws.iam.User',
    'aws.kinesis.stream': 'aws.kinesis.Stream',
    'aws.sqs.queue': 'aws.sqs.Queue',
    'aws.rds.db': 'aws.rds.DBInstance',
    'aws.rds.secgrp': 'aws.rds.DBSecurityGroup',
    'aws.redshift.cluster': 'aws.redshift.Cluster',
    'aws.route53.hostedzone': 'aws.route53.HostedZone',
    'aws.route53.healthcheck': 'aws.route53.HealthCheck',
}


def all_providers():
    providers = set()
    for resource_type in ResourceTypes:
        providers.add(resource_type.split('.')[0])
    return list(providers)


def all_services(provider_name):
    services = set()
    for resource_type in ResourceTypes:
        t = resource_type.split('.')
        if t[0] == provider_name:
            services.add(t[1])
    return list(services)


def all_types(provider_name, service_name):
    types = set()
    for resource_type in ResourceTypes:
        t = resource_type.split('.')
        if t[0] == provider_name and t[1] == service_name:
            types.add(t[2])
    return list(types)


def find_resource_class(resource_path):
    """
    dynamically load a class from a string
    """
    class_path = ResourceTypes[resource_path]
    # First prepend our __name__ to the resource string passed in.
    full_path = '.'.join([__name__, class_path])
    class_data = full_path.split(".")
    module_path = ".".join(class_data[:-1])
    class_str = class_data[-1]
    module = importlib.import_module(module_path)
    # Finally, we retrieve the Class
    return getattr(module, class_str)
