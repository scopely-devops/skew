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


class Stream(AWSResource):

    class Meta(object):
        service = 'kinesis'
        type = 'stream'
        enum_spec = ('list_streams', 'StreamNames', None)
        detail_spec = None
        id = 'StreamName'
        filter_name = None
        filter_type = None
        name = 'StreamName'
        date = None
        dimension = 'StreamName'
        tags_spec = ('list_tags_for_stream', 'Tags[]',
                     'StreamName', 'id')

    def __init__(self, client, data, query=None):
        super(Stream, self).__init__(client, data, query)
        self.data = {self.Meta.id: data}
        self._id = self.data[self.Meta.id]
