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

import os

from skew.arn import ARN

__version__ = open(os.path.join(os.path.dirname(__file__), '_version')).read()


def scan(sku, **kwargs):
    """
    Scan (i.e. look up) a SKU.

    The main interface into the skew library.  Pass in a SKU and we try
    to look it up and return the appropriate data.

    Each SKU scheme should be implemented as a class.  That class should
    have an attribute called ``RegEx``.  The lookup method simply tries
    to match the SKU with the ``RegEx`` of the scheme.  If it matches,
    an instance of the class is created by passing in the ``groupdict``
    of the regular expression to the constructor.  The scheme class
    should also implement the ``iterator`` protocol because people
    will want to iterate over the scheme object to get their results.

    We could use some sort of dynamic loading of scheme classes
    but since there is currently only one (ARN) let's not over-complicate
    things.
    """
    return ARN(sku, **kwargs)
