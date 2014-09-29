# Copyright 2014 Scopely, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import jmespath

from skew.exception import ClientError, ServerError


class Endpoint(object):
    """
    Represents an endpoint of a service.
    """

    def __init__(self, service, region, account):
        self.service = service
        self.region = region
        self.account = account
        self._endpoint = self.service.get_endpoint(self.region)

    def __repr__(self):
        return '%s:%s:%s' % (self.service, self.region, self.account)

    def call(self, op_name, query=None, **kwargs):
        """
        Make a request to this service endpoint.  The response data is
        returned from this call as native Python data structures.

        This method differs from the ``call`` method of the
        ``Operation`` object in botocore in the following ways:

          * The HTTP response is checked and if there is a 400
            or 500 response code it will raise an exception.
          * It automatically handles the pagination rather than
            relying on a separate pagination method call.
          * You can pass an optional jmespath query and this query
            will be applied to the data returned from the low-level
            call.  This allows you to tailor the returned data to be
            exactly what you want.

        :type op_name: str
        :param op_name: The name of the request you wish to make.

        :type query: str
        :param query: A jmespath query that will be applied to the
            data returned by the operation prior to returning
            it to the user.

        :type kwargs: keyword arguments
        :param kwargs: Additional keyword arguments you want to pass
            to the service when making the request.
        """
        if query:
            query = jmespath.compile(query)
        op = self.service.get_operation(op_name)
        if op.can_paginate:
            pages = op.paginate(self._endpoint, **kwargs)
            data = pages.build_full_result()
        else:
            http_response, data = op.call(self._endpoint, **kwargs)
            if http_response.status_code >= 500:
                raise ServerError(http_response.status_code, data, op_name)
            if http_response.status_code >= 400:
                raise ClientError(http_response.status_code, data, op_name)
        if query:
            data = query.search(data)
        return data
