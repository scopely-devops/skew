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


class StateMachines(AWSResource):
    class Meta(object):
        service = "stepfunctions"
        type = "stateMachine"
        enum_spec = ("list_state_machines", "stateMachines[]", None)
        detail_spec = ("describe_state_machine", None, "stateMachineArn", "arn")
        filter_name = None
        filter_type = None
        id = "name"
        name = "name"
        date = "creationDate"
        tags_spec = ("list_tags_for_resource", "tags", "resourceArn", "arn")

    @classmethod
    def filter(cls, arn, resource_id, data):
        return resource_id == data["name"]

    def __init__(self, client, data, query=None):
        super(StateMachines, self).__init__(client, data, query)
        self._arn = self._data["stateMachineArn"]

        detail = self._feed_from_spec(attr_spec=self.Meta.detail_spec)
        if "ResponseMetadata" in detail:
            del detail["ResponseMetadata"]

        self._data = {
            **self._data,
            **detail,
        }

    @property
    def arn(self):
        return self._arn