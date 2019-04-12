# Copyright (c) 2014 Scopely, Inc.
# Copyright (c) 2015 Mitch Garnaat
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
import jmespath
import logging
from skew.resources.aws import AWSResource

LOG = logging.getLogger(__name__)


class CloudTrail(AWSResource):

    class Meta(object):
        service = 'cloudtrail'
        type = 'trail'
        enum_spec = ('describe_trails', 'trailList[]', None)
        attr_spec = None
        detail_spec = None
        id = 'Name'
        tags_spec = ('list_tags', 'ResourceTagList[].TagsList[]',
                     'ResourceIdList', 'name')
        filter_name = 'trailNameList'
        filter_type = 'arn'
        name = 'TrailARN'
        date = None
        dimension = None
