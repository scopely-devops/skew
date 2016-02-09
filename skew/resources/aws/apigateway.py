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

import logging

from skew.resources.aws import AWSResource

LOG = logging.getLogger(__name__)


class RestAPI(AWSResource):

    class Meta(object):
        service = 'apigateway'
        type = 'restapis'
        enum_spec = ('get_rest_apis', 'items', None)
        id = 'id'
        filter_name = None
        filter_type = None
        detail_spec = None
        name = 'name'
        date = 'createdDate'
        dimension = 'GatewayName'

    @classmethod
    def filter(cls, arn, resource_id, data):
        api_id = data.get(cls.Meta.id)
        LOG.debug('%s == %s', resource_id, api_id)
        return resource_id == api_id
