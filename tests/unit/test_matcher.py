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
import unittest

from skew.utils import Matcher


class TestMatcher(unittest.TestCase):

    def setUp(self):
        self.choices = ['foo', 'bar', 'fie', 'baz']

    def tearDown(self):
        pass

    def test_explicit(self):
        matcher = Matcher(self.choices, 'fie')
        matches = list(matcher)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0], 'fie')

    def test_single_match(self):
        matcher = Matcher(self.choices, 'ba.*')
        matches = list(matcher)
        self.assertEqual(len(matches), 2)
        self.assertIn('bar', matches)
        self.assertIn('baz', matches)

    def test_wildcard(self):
        matcher = Matcher(self.choices, '*')
        matches = list(matcher)
        self.assertEqual(len(matches), 4)
        self.assertIn('foo', matches)
        self.assertIn('fie', matches)
        self.assertIn('bar', matches)
        self.assertIn('baz', matches)

    def test_no_match(self):
        matcher = Matcher(self.choices, 'nomatch')
        matches = list(matcher)
        self.assertEqual(len(matches), 0)
