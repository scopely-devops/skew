# Copyright (c) 2014 Scopely, Inc.
# Copyright (c) 2015 Mitch Garnaat
# Copyright (c) 2019 Christophe Morio
# Copyright (c) 2020 Jerome Guibert
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


class Identity(AWSResource):
    class Meta(object):
        service = "ses"
        type = "identity"
        enum_spec = ("list_identities", "Identities", None)
        detail_spec = ("describe_table", "TableName", "Table")
        id = "Identity"
        tags_spec = None
        filter_name = None
        name = "IdentityName"
        date = None
        dimension = "IdentityName"

    def __init__(self, client, data, query=None):
        super(Identity, self).__init__(client, data, query)
        arn = self._data
        self._data = {"IdentityName": arn}

    @property
    def arn(self):
        return "arn:aws:%s:%s:%s:%s/%s" % (
            self._client.service_name,
            self._client.region_name,
            self._client.account_id,
            self.resourcetype,
            self._data["IdentityName"],
        )
