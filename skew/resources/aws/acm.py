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

import logging

import jmespath

from skew.resources.aws import AWSResource


LOG = logging.getLogger(__name__)


class Certificate(AWSResource):

    class Meta(object):
        service = 'acm'
        type = 'certificate'
        enum_spec = ('list_certificates', 'CertificateSummaryList', None)
        detail_spec = ('describe_certificate', 'CertificateArn', 'Certificate')
        id = 'CertificateArn'
        tags_spec = ('list_tags_for_certificate', 'Tags[]',
                     'CertificateArn', 'id')
        filter_name = None
        name = 'DomainName'
        date = 'CreatedAt'
        dimension = None

    @classmethod
    def filter(cls, arn, resource_id, data):
        certificate_id = data.get(cls.Meta.id).split('/')[-1]
        LOG.debug('%s == %s', resource_id, certificate_id)
        return resource_id == certificate_id

    @property
    def arn(self):
        return self.data['CertificateArn']

    def __init__(self, client, data, query=None):
        super(Certificate, self).__init__(client, data, query)

        self._id = data['CertificateArn']

        detail_op, param_name, detail_path = self.Meta.detail_spec
        params = {param_name: data['CertificateArn']}
        data = client.call(detail_op, **params)

        self.data = jmespath.search(detail_path, data)
