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


class Alarm(AWSResource):

    class Meta(object):
        service = 'cloudwatch'
        type = 'alarm'
        enum_spec = ('describe_alarms', 'MetricAlarms', None)
        id = 'AlarmArn'
        filter_name = 'AlarmNames'
        filter_type = 'list'
        detail_spec = None
        name = 'AlarmName'
        date = 'AlarmConfigurationUpdatedTimestamp'
        dimension = None
