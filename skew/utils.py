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

import logging
import re

LOG = logging.getLogger(__name__)


class Matcher(object):
    """
    Given a list of possible values and a regular expression
    this object acts as an iterator to return all matches.
    """

    def __init__(self, choices, regular_expression):
        self._matches = []
        self.name = regular_expression
        if regular_expression == '*':
            regular_expression = '.*'
        regex = re.compile(regular_expression)
        for choice in choices:
            if regex.search(choice):
                self._matches.append(choice)

    def __repr__(self):
        return self.name

    def __iter__(self):
        for match in self._matches:
            yield match
