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

from skew.resources.aws import AWSResource


class Route53Resource(AWSResource):

    @property
    def arn(self):
        return 'arn:aws:%s:::%s/%s' % (
            self._client.service_name, self.resourcetype, self.id)


class HostedZone(Route53Resource):

    class Meta(object):
        service = 'route53'
        type = 'hostedzone'
        enum_spec = ('list_hosted_zones', 'HostedZones', None)
        detail_spec = ('GetHostedZone', 'Id', None)
        id = 'Id'
        filter_name = None
        name = 'Name'
        date = None
        dimension = None
        tags_spec = ('list_tags_for_resource', 'ResourceTagSet.Tags[]',
                     'ResourceId', 'id', {'ResourceType': 'hostedzone'})

    @property
    def id(self):
        return self._id.split('/')[-1]


class HealthCheck(Route53Resource):

    class Meta(object):
        service = 'route53'
        type = 'healthcheck'
        enum_spec = ('list_health_checks', 'HealthChecks', None)
        detail_spec = ('GetHealthCheck', 'Id', None)
        id = 'Id'
        filter_name = None
        name = None
        date = None
        dimension = None
        tags_spec = ('list_tags_for_resource', 'ResourceTagSet.Tags[]',
                     'ResourceId', 'id', {'ResourceType': 'healthcheck'})


class ResourceRecordSet(Route53Resource):

    class Meta(object):
        service = 'route53'
        type = 'rrset'
        enum_spec = ('list_resource_record_sets', 'ResourceRecordSets', None)
        detail_spec = None
        id = 'Name'
        filter_name = None
        name = 'Name'
        date = None
        dimension = None
