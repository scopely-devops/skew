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

import jmespath

from skew.resources.aws import AWSResource


class ElasticsearchDomain(AWSResource):

    class Meta(object):
        service = 'es'
        type = 'domain'
        enum_spec = ('list_domain_names', 'DomainNames[].DomainName', None)
        tags_spec = ('list_tags', 'TagList',
                     'ARN', 'arn')
        detail_spec = ('describe_elasticsearch_domain', 'DomainName', 'DomainStatus')
        id = 'DomainName'
        filter_name = None
        name = 'DomainName'
        date = None
        dimension = 'DomainName'

    def __init__(self, client, data, query=None):
        super(ElasticsearchDomain, self).__init__(client, data, query)
        self._id = data
        detail_op, param_name, detail_path = self.Meta.detail_spec
        params = {param_name: self.id}
        data = client.call(detail_op, **params)
        self.data = jmespath.search(detail_path, data)
