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

from skew.resources.aws import AWSResource


class HostedZone(AWSResource):

    class Meta(object):
        service = 'route53'
        type = 'hostedzone'
        enum_spec = ('ListHostedZones', 'HostedZones')
        detail_spec = ('GetHostedZone', 'id', None)
        id = 'Id'
        filter_name = None
        name = 'Name'
        date = None
        dimension = None

    @property
    def id(self):
        return self._id.split('/')[-1]


class HealthCheck(AWSResource):

    class Meta(object):
        service = 'route53'
        type = 'healthcheck'
        enum_spec = ('ListHealthChecks', 'HealthChecks')
        detail_spec = ('GetHealthCheck', 'id', None)
        id = 'Id'
        filter_name = None
        name = None
        date = None
        dimension = None


class ResourceRecordSet(AWSResource):

    class Meta(object):
        service = 'route53'
        type = 'rrset'
        enum_spec = ('ListResourceRecordSets', 'ResourceRecordSets')
        detail_spec = None
        id = 'Name'
        filter_name = None
        name = 'Name'
        date = None
        dimension = None
