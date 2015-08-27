# Copyright 2014 Scopely, Inc.
# Copyright (c) 2015 Mitch Garnaat
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


class ConfigNotFoundError(Exception):

    pass


class BaseOperationError(Exception):

    def __init__(self, error_code, error_body, operation_name):
        msg = 'Error(%d) when calling (%s): %s' % (error_code,
                                                   operation_name,
                                                   error_body)
        super(BaseOperationError, self).__init__(msg)
        self.error_code = error_code
        self.error_body = error_body
        self.operation_name = operation_name


class ClientError(BaseOperationError):
    pass


class ServerError(BaseOperationError):
    pass
