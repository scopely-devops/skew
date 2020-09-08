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

import jmespath

class DeliveryStream(AWSResource):

    class Meta(object):
        service = 'firehose'
        type = 'deliverystream'
        enum_spec = ('list_delivery_streams', 'DeliveryStreamNames', None)
        detail_spec = ('describe_delivery_stream', 'DeliveryStreamName', 'DeliveryStreamDescription')
        id = 'DeliveryStreamName'
        filter_name = None
        filter_type = None
        name = 'DeliveryStreamName'
        date = 'CreateTimestamp'
        dimension = 'DeliveryStreamName'
        tags_spec = ('list_tags_for_delivery_stream', 'Tags[]', 'DeliveryStreamName', 'id')

    def __init__(self, client, data, query=None):
        super(DeliveryStream, self).__init__(client, data, query)
        self._id = data
        detail_op, param_name, detail_path = self.Meta.detail_spec
        params = {param_name: self.id}
        data = client.call(detail_op, **params)
        self.data = jmespath.search(detail_path, data)
