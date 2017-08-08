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

from skew.resources.aws import AWSResource


class Cluster(AWSResource):

    class Meta(object):
        service = 'elasticache'
        type = 'cluster'
        enum_spec = ('describe_cache_clusters',
                     'CacheClusters[]', None)
        detail_spec = None
        id = 'CacheClusterId'
        tags_spec = ('list_tags_for_resource', 'TagList',
                     'ResourceName', 'arn')
        filter_name = 'CacheClusterId'
        filter_type = 'scalar'
        name = 'CacheClusterId'
        date = 'CacheClusterCreateTime'
        dimension = 'CacheClusterId'

    @property
    def arn(self):
        return 'arn:aws:%s:%s:%s:%s:%s' % (
            self._client.service_name,
            self._client.region_name,
            self._client.account_id, self.resourcetype, self.id)


class SubnetGroup(AWSResource):

    class Meta(object):
        service = 'elasticache'
        type = 'subnet-group'
        enum_spec = ('describe_cache_subnet_groups',
                     'CacheSubnetGroups', None)
        detail_spec = None
        id = 'CacheSubnetGroupName'
        filter_name = 'CacheSubnetGroupName'
        filter_type = 'scalar'
        name = 'CacheSubnetGroupName'
        date = None
        dimension = None


class Snapshot(AWSResource):

    class Meta(object):
        service = 'elasticache'
        type = 'snapshot'
        enum_spec = ('describe_snapshots', 'Snapshots', None)
        detail_spec = None
        id = 'SnapshotName'
        tags_spec = ('list_tags_for_resource', 'TagList',
                     'ResourceName', 'arn')
        filter_name = 'SnapshotName'
        filter_type = 'scalar'
        name = 'SnapshotName'
        date = 'StartTime'
        dimension = None

    @property
    def arn(self):
        return 'arn:aws:%s:%s:%s:%s:%s' % (
            self._client.service_name,
            self._client.region_name,
            self._client.account_id, self.resourcetype, self.id)
