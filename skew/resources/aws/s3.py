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
import jmespath

from skew.resources.aws import AWSResource


class Bucket(AWSResource):

    class Meta(object):
        service = 's3'
        type = 'bucket'
        enum_spec = ('list_buckets', 'Buckets[]', None)
        detail_spec = ('list_objects', 'Bucket', 'Contents[]')
        id = 'Name'
        filter_name = None
        name = 'BucketName'
        date = 'CreationDate'
        dimension = None

    def __init__(self, client, data, query=None):
        super(Bucket, self).__init__(client, data, query)
        self._data = data
        self._keys = []

    def __iter__(self):
        detail_op, param_name, detail_path = self.Meta.detail_spec
        params = {param_name: self.id}
        if not self._keys:
            data = self._client.call(detail_op, **params)
            self._keys = jmespath.search(detail_path, data)
        for key in self._keys:
            yield key
