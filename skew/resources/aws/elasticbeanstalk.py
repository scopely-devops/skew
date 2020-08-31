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


class Application(AWSResource):
    class Meta(object):
        service = 'elasticbeanstalk'
        type = 'application'
        enum_spec = ('describe_applications', 'Applications', None)
        detail_spec = None
        id = 'ApplicationName'
        filter_name = None
        filter_type = None
        name = 'ApplicationName'
        date = None
        dimension = None
        tags_spec = ('list_tags_for_resource', 'ResourceTags[]',
                     'ResourceArn', 'arn')


class Environment(AWSResource):
    class Meta(object):
        service = 'elasticbeanstalk'
        type = 'environment'
        enum_spec = ('describe_environments', 'Environments', None)
        detail_spec = None
        id = 'EnvironmentName'
        filter_name = None
        filter_type = None
        name = 'EnvironmentName'
        date = None
        dimension = None
        tags_spec = ('list_tags_for_resource', 'ResourceTags[]',
                     'ResourceArn', 'arn')

    @property
    def arn(self):
        return 'arn:aws:%s:%s:%s:%s/%s/%s' % (
            self._client.service_name,
            self._client.region_name,
            self._client.account_id,
            self.resourcetype,
            self.data['ApplicationName'],
            self.id
        )
