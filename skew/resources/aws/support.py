# Copyright (c) 2014 Scopely, Inc.
# Copyright (c) 2015 Mitch Garnaat
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


class Check(AWSResource):
    class Meta(object):
        service = "support"
        type = "check"
        enum_spec = ("describe_trusted_advisor_checks", "checks", None)
        detail_spec = None
        id = "id"
        tags_spec = None
        filter_name = None
        name = "name"
        date = None
        dimension = "IdentityName"
