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


class Stream(AWSResource):

    class Meta(object):
        service = 'kinesis'
        type = 'stream'
        enum_spec = ('ListStreams', 'StreamNames')
        detail_spec = None
        id = 'StreamName'
        filter_name = None
        filter_type = None
        name = 'StreamName'
        date = None
        dimension = 'StreamName'

    def __init__(self, endpoint, data, query=None):
        super(Stream, self).__init__(endpoint, data, query)
        self.data = {self.Meta.id: data}
        self._id = self.data[self.Meta.id]
