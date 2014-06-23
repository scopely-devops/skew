# Copyright (c) 2014 Mitch Garnaat http://garnaat.org/
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

import os
import glob
import imp
import inspect
import logging
import re

LOG = logging.getLogger(__name__)


class DynamicLoader(object):

    def __init__(self, keyfn, path):
        self._keyfn = keyfn
        self._file = os.path.basename(path)
        self._dirname = os.path.dirname(path)
        self._path = [self._dirname]
        self._cache = {}

    def load_classes(self):
        py_files = glob.glob(
            os.path.join(self._dirname, '*.py'))
        for f in py_files:
            mod_name = os.path.basename(f)
            mod_name = os.path.splitext(mod_name)[0]
            if mod_name == os.path.splitext(self._file)[0]:
                continue
            t = imp.find_module(mod_name, self._path)
            module = imp.load_module(mod_name, t[0], t[1], t[2])
            clsmembers = inspect.getmembers(module, inspect.isclass)
            for clsname, cls in clsmembers:
                key = self._keyfn(cls)
                if key:
                    self._cache[key] = cls

    def find_class(self, key):
        return self._cache[key]

    def all_keys(self):
        return self._cache.keys()

    def all_classes(self):
        return self._cache.values()

    def all_items(self):
        return self._cache.items()


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
