# Copyright (c) 2015 Scopely, Inc.
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
import unittest

import mock

from skew.arn import ARNComponent


class FooBarComponent(ARNComponent):

    def choices(self, context=None):
        if context:
            if 'sorted' in context:
                choices = ['bar', 'baz', 'fie', 'foo']
        else:
            choices = ['foo', 'bar', 'fie', 'baz']
        return choices


class TestARNComponent(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_choices(self):
        foobar = FooBarComponent('*', None)
        self.assertEqual(foobar.choices(), ['foo', 'bar', 'fie', 'baz'])
        self.assertEqual(foobar.choices(
            context=['sorted']), ['bar', 'baz', 'fie', 'foo'])
        self.assertEqual(foobar.pattern, '*')
        self.assertEqual(foobar.matches(), ['foo', 'bar', 'fie', 'baz'])
        foobar.pattern = 'f.*'
        self.assertEqual(foobar.pattern, 'f.*')
        self.assertEqual(foobar.matches(), ['foo', 'fie'])
        self.assertEqual(foobar.complete('b'), ['bar', 'baz'])
